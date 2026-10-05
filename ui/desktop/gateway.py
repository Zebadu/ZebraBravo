from capabilities.contracts import CapabilityResult
from collections.abc import Mapping

from pywinauto import Desktop
import win32con
import win32gui
import win32ui


class DesktopGateway:
    """Read-only gateway to the Windows desktop through UI Automation."""

    def __init__(self, backend="uia"):
        self.backend = backend

    def execute(self, request):
        if not isinstance(request, Mapping):
            return CapabilityResult(
                ok=False,
                message="Desktop request must be a mapping.",
                code="invalid_request",
            )

        operation = request.get("operation")

        if operation == "inspect":
            return CapabilityResult(
                ok=True,
                data=self.inspect(),
            )

        if operation == "capture":
            return self.capture(request.get("title"))

        if operation == "read_terminal":
            return self.read_terminal(
                title=request.get("title", "Windows PowerShell"),
                limit=request.get("limit", 12000),
            )

        return CapabilityResult(
            ok=False,
            message=f"Unsupported desktop operation: {operation}",
            code="unsupported_operation",
        )

    def capture(self, title=None):
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

            screen_dc = win32gui.GetDC(0)
            source_dc = win32ui.CreateDCFromHandle(screen_dc)
            memory_dc = source_dc.CreateCompatibleDC()

            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(source_dc, width, height)
            memory_dc.SelectObject(bitmap)

            memory_dc.BitBlt(
                (0, 0),
                (width, height),
                source_dc,
                (left, top),
                win32con.SRCCOPY,
            )

            image = bitmap.GetBitmapBits(True)

            return CapabilityResult(
                ok=True,
                data={
                    "title": title or "Windows Desktop",
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
                win32gui.ReleaseDC(0, screen_dc)
            except Exception:
                pass

            try:
                win32gui.DeleteObject(bitmap.GetHandle())
            except Exception:
                pass

    def read_terminal(self, title="Windows PowerShell", limit=12000):
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return CapabilityResult(
                ok=False,
                message="Terminal text limit must be an integer.",
                code="invalid_request",
            )

        limit = max(1, min(limit, 100000))

        try:
            import comtypes.client

            desktop = Desktop(backend=self.backend)
            window = desktop.window(title_re=title)

            if not window.exists():
                return CapabilityResult(
                    ok=False,
                    message=f"Desktop window not found: {title}",
                    code="window_not_found",
                )

            terminal = window.child_window(
                control_type="Text",
                class_name="TermControl",
            )

            if not terminal.exists():
                return CapabilityResult(
                    ok=False,
                    message="Terminal control not found.",
                    code="terminal_not_found",
                )

            wrapper = terminal.wrapper_object()
            element = wrapper.element_info.element

            automation = comtypes.client.GetModule("UIAutomationCore.dll")
            pattern = element.GetCurrentPattern(10014).QueryInterface(
                automation.IUIAutomationTextPattern
            )

            text = pattern.DocumentRange.GetText(-1)
            text = text.rstrip()

            if len(text) > limit:
                text = text[-limit:]
                truncated = True
            else:
                truncated = False

            return CapabilityResult(
                ok=True,
                data={
                    "title": window.window_text(),
                    "control": "TermControl",
                    "text": text,
                    "length": len(text),
                    "truncated": truncated,
                },
            )

        except Exception as error:
            return CapabilityResult(
                ok=False,
                message=str(error),
                code="terminal_read_failed",
            )

    def inspect(self):
        desktop = Desktop(backend=self.backend)
        windows = desktop.windows()

        return [
            {
                "title": window.window_text(),
                "control_type": window.element_info.control_type,
                "visible": window.is_visible(),
                "enabled": window.is_enabled(),
            }
            for window in windows
        ]