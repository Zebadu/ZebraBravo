import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"

sys.path.insert(0, str(MODULES_DIR))

from capabilities.runtime import CapabilityRuntime


runtime = CapabilityRuntime(
    workspace_root=PROJECT_ROOT,
    permissions={
        "filesystem.read",
        "filesystem.write",
        "git.read",
    },
)

runtime.development_service.set_development_mode(True)

development = runtime.development_service.development_interface

read_result = development.execute(
    "read",
    {
        "path": "ui/desktop/gateway.py",
    },
)

if not read_result.ok:
    raise RuntimeError(
        f"Could not read gateway.py: "
        f"{read_result.code}: {read_result.message}"
    )

content = read_result.data["content"]

if "import win32con" not in content:
    content = content.replace(
        "from pywinauto import Desktop",
        "from pywinauto import Desktop\n"
        "import win32con\n"
        "import win32gui\n"
        "import win32ui",
        1,
    )

if "    def capture(self, title=None):" not in content:
    marker = "    def inspect(self):"

    method = """    def capture(self, title=None):
        hwnd = None

        if title:
            desktop = Desktop(backend=self.backend)
            window = desktop.window(title_re=title)

            if not window.exists():
                return CapabilityResult(
                    ok=False,
                    message=f"Desktop window not found: {title}",
                    code="window_not_found",
                )

            hwnd = window.handle
        else:
            hwnd = win32gui.GetDesktopWindow()

        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top

            if width <= 0 or height <= 0:
                return CapabilityResult(
                    ok=False,
                    message="Capture target has invalid dimensions.",
                    code="capture_failed",
                )

            window_dc = win32gui.GetWindowDC(hwnd)
            source_dc = win32ui.CreateDCFromHandle(window_dc)
            memory_dc = source_dc.CreateCompatibleDC()

            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(source_dc, width, height)
            memory_dc.SelectObject(bitmap)

            memory_dc.BitBlt(
                (0, 0),
                (width, height),
                source_dc,
                (0, 0),
                win32con.SRCCOPY,
            )

            image = bitmap.GetBitmapBits(True)

            return CapabilityResult(
                ok=True,
                data={
                    "title": title,
                    "left": left,
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "width": width,
                    "height": height,
                    "format": "BGRA",
                    "bytes": image,
                },
            )

        except Exception as error:
            return CapabilityResult(
                ok=False,
                message=str(error),
                code="capture_failed",
            )

        finally:
            try:
                memory_dc.DeleteDC()
            except Exception:
                pass

            try:
                source_dc.DeleteDC()
            except Exception:
                pass

            try:
                win32gui.ReleaseDC(hwnd, window_dc)
            except Exception:
                pass

            try:
                win32gui.DeleteObject(bitmap.GetHandle())
            except Exception:
                pass

"""

    if content.count(marker) != 1:
        raise RuntimeError(
            "Expected exactly one inspect method."
        )

    content = content.replace(
        marker,
        method + marker,
        1,
    )

if 'if operation == "capture":' not in content:
    target = """        if operation == "inspect":
            return CapabilityResult(
                ok=True,
                data=self.inspect(),
            )

"""

    replacement = target + """        if operation == "capture":
            return CapabilityResult(
                ok=True,
                data=self.capture(request.get("title")),
            )

"""

    if target not in content:
        raise RuntimeError(
            "Expected inspect dispatch block was not found."
        )

    content = content.replace(
        target,
        replacement,
        1,
    )

write_result = development.execute(
    "write",
    {
        "path": "ui/desktop/gateway.py",
        "content": content,
    },
)

print(
    "GOVERNED WRITE:",
    write_result.ok,
    write_result.code,
    write_result.message,
)

if write_result.ok:
    print(write_result.data)