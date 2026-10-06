param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("project_info", "read", "write", "search")]
    [string]$Operation,

    [Parameter(Mandatory = $false)]
    [string]$Query,

    [Parameter(Mandatory = $false)]
    [string]$Path,

    [Parameter(Mandatory = $false)]
    [string]$Content
)

$ErrorActionPreference = "Stop"

$python = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
$entrypoint = Join-Path $PSScriptRoot "..\modules\synapse\powershell_entry.py"

$payload = @{}

if ($Query) {
    $payload.query = $Query
}

if ($Path) {
    $payload.path = $Path
}

if ($null -ne $Content) {
    $payload.content = $Content
}

$env:ZEBRALINK_PAYLOAD = $payload | ConvertTo-Json -Compress

& $python $entrypoint $Operation

Remove-Item Env:ZEBRALINK_PAYLOAD -ErrorAction SilentlyContinue
