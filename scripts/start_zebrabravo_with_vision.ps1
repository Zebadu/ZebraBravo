$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$workerRoot = "C:\Users\qst4t\Documents\ComfyUI"
$workerPython = Join-Path $workerRoot ".venv\Scripts\python.exe"
$workerScript = Join-Path $workerRoot "vision_worker.py"
$appPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$workerPort = 52337
$worker = $null

$oldToken = $env:ZEBRABRAVO_VISION_TOKEN
$oldEnabled = $env:ZEBRABRAVO_VISION_ENABLED
$oldUrl = $env:ZEBRABRAVO_VISION_URL
$oldPythonPath = $env:PYTHONPATH

function Test-LoopbackPort {
    param([int]$Port)
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $pending = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        if (-not $pending.AsyncWaitHandle.WaitOne(300)) { return $false }
        $client.EndConnect($pending)
        return $client.Connected
    } catch {
        return $false
    } finally {
        $client.Close()
    }
}

try {
    foreach ($path in @($workerPython, $workerScript, $appPython)) {
        if (-not (Test-Path $path)) {
            throw "Required file not found: $path"
        }
    }

    if (Test-LoopbackPort -Port $workerPort) {
        throw "Port $workerPort is already in use. No existing process was touched."
    }

    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    $token = [Convert]::ToBase64String($bytes)

    $env:ZEBRABRAVO_VISION_TOKEN = $token
    $env:ZEBRABRAVO_VISION_ENABLED = "1"
    $env:ZEBRABRAVO_VISION_URL = "http://127.0.0.1:$workerPort/describe"
    $env:PYTHONPATH = Join-Path $projectRoot "modules"

    $logTag = [Guid]::NewGuid().ToString("N")
    $workerOut = Join-Path $env:TEMP "zebrabravo-eyes-$logTag.out.log"
    $workerErr = Join-Path $env:TEMP "zebrabravo-eyes-$logTag.err.log"

    Write-Host "Starting local EYES worker..."
    $worker = Start-Process `
        -FilePath $workerPython `
        -ArgumentList ('"' + $workerScript + '"') `
        -WorkingDirectory $workerRoot `
        -PassThru `
        -RedirectStandardOutput $workerOut `
        -RedirectStandardError $workerErr

    $ready = $false
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Milliseconds 500
        if ($worker.HasExited) {
            throw "Vision worker exited during startup. Inspect logs: $workerErr"
        }
        if (Test-LoopbackPort -Port $workerPort) {
            $ready = $true
            break
        }
    }

    if (-not $ready) {
        throw "Vision worker did not open its port within 30 seconds. Inspect logs: $workerErr"
    }

    Write-Host "PASS: EYES worker listening on loopback."
    Write-Host "Starting ZebraBravo with vision enabled for this session."
    Write-Host "Exit ZebraBravo normally to stop its worker."

    $app = Start-Process `
        -FilePath $appPython `
        -ArgumentList @("core\main.py") `
        -WorkingDirectory $projectRoot `
        -NoNewWindow `
        -PassThru `
        -Wait

    if ($app.ExitCode -ne 0) {
        throw "ZebraBravo exited with code $($app.ExitCode)."
    }
}
finally {
    if ($worker -and -not $worker.HasExited) {
        Write-Host "Stopping the EYES worker started by this launcher..."
        Stop-Process -Id $worker.Id -ErrorAction SilentlyContinue
        $worker.WaitForExit()
    }

    $env:ZEBRABRAVO_VISION_TOKEN = $oldToken
    $env:ZEBRABRAVO_VISION_ENABLED = $oldEnabled
    $env:ZEBRABRAVO_VISION_URL = $oldUrl
    $env:PYTHONPATH = $oldPythonPath

    Write-Host "Session vision variables restored."
}
