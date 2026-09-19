from __future__ import annotations

from collections.abc import Mapping
from typing import Any

try:
    import winreg
except ImportError:  # pragma: no cover - Windows-only capability
    winreg = None

from capabilities.context import CapabilityContext
from capabilities.contracts import CapabilityMetadata, CapabilityResult


class WindowsDiagnosticsCapability:
    """Governed, read-only Windows host diagnostics."""

    _UNINSTALL_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    _ALLOWED_OPERATIONS = {"software_lookup"}

    def __init__(self) -> None:
        self.metadata = CapabilityMetadata(
            name="windows_diagnostics",
            description=(
                "Read-only Windows diagnostics for narrowly scoped host inspection, "
                "including installed-software lookup."
            ),
            required_permissions=frozenset({"windows.diagnostics.read"}),
            side_effect="read",
        )

    def execute(
        self,
        request: Mapping[str, Any],
        context: CapabilityContext,
    ) -> CapabilityResult:
        operation = request.get("operation")

        if operation not in self._ALLOWED_OPERATIONS:
            return CapabilityResult(
                ok=False,
                code="unsupported_operation",
                message=f"Unsupported windows_diagnostics operation: {operation!r}",
            )

        if winreg is None:
            return CapabilityResult(
                ok=False,
                code="platform_unsupported",
                message="windows_diagnostics requires Windows.",
            )

        if operation == "software_lookup":
            name = request.get("name")

            if not isinstance(name, str) or not name.strip():
                return CapabilityResult(
                    ok=False,
                    code="invalid_request",
                    message="software_lookup requires a non-empty 'name'.",
                )

            query = name.strip()
            matches: list[dict[str, Any]] = []

            for source, root, view in self._registry_locations():
                matches.extend(
                    self._read_location(
                        source=source,
                        root=root,
                        view=view,
                        query=query,
                    )
                )

            return CapabilityResult(
                ok=True,
                code="ok",
                message=f"Windows software lookup completed for {query!r}.",
                data={
                    "operation": operation,
                    "query": query,
                    "matches": matches,
                    "match_count": len(matches),
                },
            )

        return CapabilityResult(
            ok=False,
            code="unsupported_operation",
            message=f"Unsupported windows_diagnostics operation: {operation!r}",
        )

    def _registry_locations(self):
        assert winreg is not None

        return [
            (
                "HKLM-64",
                winreg.HKEY_LOCAL_MACHINE,
                getattr(winreg, "KEY_WOW64_64KEY", 0),
            ),
            (
                "HKLM-32",
                winreg.HKEY_LOCAL_MACHINE,
                getattr(winreg, "KEY_WOW64_32KEY", 0),
            ),
            (
                "HKCU",
                winreg.HKEY_CURRENT_USER,
                0,
            ),
        ]

    def _read_location(
        self,
        *,
        source: str,
        root: Any,
        view: int,
        query: str,
    ) -> list[dict[str, Any]]:
        assert winreg is not None

        results: list[dict[str, Any]] = []
        query_folded = query.casefold()

        try:
            with winreg.OpenKey(
                root,
                self._UNINSTALL_PATH,
                0,
                winreg.KEY_READ | view,
            ) as uninstall_root:

                index = 0

                while True:
                    try:
                        subkey_name = winreg.EnumKey(uninstall_root, index)
                    except OSError:
                        break

                    index += 1

                    try:
                        with winreg.OpenKey(
                            uninstall_root,
                            subkey_name,
                            0,
                            winreg.KEY_READ,
                        ) as app_key:

                            display_name = self._value(
                                app_key,
                                "DisplayName",
                            )

                            if not isinstance(display_name, str):
                                continue

                            if query_folded not in display_name.casefold():
                                continue

                            results.append(
                                {
                                    "display_name": display_name,
                                    "display_version": self._value(
                                        app_key,
                                        "DisplayVersion",
                                    ),
                                    "publisher": self._value(
                                        app_key,
                                        "Publisher",
                                    ),
                                    "install_date": self._value(
                                        app_key,
                                        "InstallDate",
                                    ),
                                    "install_location": self._value(
                                        app_key,
                                        "InstallLocation",
                                    ),
                                    "uninstall_string": self._value(
                                        app_key,
                                        "UninstallString",
                                    ),
                                    "registry_source": source,
                                    "registry_subkey": subkey_name,
                                }
                            )

                    except OSError:
                        continue

        except OSError:
            return []

        return results

    @staticmethod
    def _value(key: Any, name: str) -> Any:
        assert winreg is not None

        try:
            value, _ = winreg.QueryValueEx(key, name)
            return value
        except OSError:
            return None
