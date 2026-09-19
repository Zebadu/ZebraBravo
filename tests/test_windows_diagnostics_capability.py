import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "modules"))

from capabilities.context import CapabilityContext
from capabilities.plugins.windows_diagnostics import WindowsDiagnosticsCapability


def test_windows_diagnostics_has_expected_metadata():
    capability = WindowsDiagnosticsCapability()

    assert capability.metadata.name == "windows_diagnostics"
    assert capability.metadata.required_permissions == {
        "windows.diagnostics.read"
    }
    assert capability.metadata.side_effect == "read"


def test_windows_diagnostics_allows_direct_read_with_context():
    capability = WindowsDiagnosticsCapability()

    result = capability.execute(
        {"operation": "software_lookup", "name": "Macrium"},
        CapabilityContext(),
    )

    assert result.ok is True
    assert result.code == "ok"


def test_windows_diagnostics_rejects_unknown_operation():
    capability = WindowsDiagnosticsCapability()

    result = capability.execute(
        {"operation": "launch_missiles", "name": "Macrium"},
        CapabilityContext(
            permissions={"windows.diagnostics.read"},
        ),
    )

    assert result.ok is False
    assert result.code == "unsupported_operation"


def test_windows_diagnostics_requires_an_operation():
    capability = WindowsDiagnosticsCapability()

    result = capability.execute(
        {"name": "Macrium"},
        CapabilityContext(
            permissions={"windows.diagnostics.read"},
        ),
    )

    assert result.ok is False
    assert result.code == "unsupported_operation"


def test_windows_diagnostics_requires_a_name():
    capability = WindowsDiagnosticsCapability()

    result = capability.execute(
        {"operation": "software_lookup"},
        CapabilityContext(
            permissions={"windows.diagnostics.read"},
        ),
    )

    assert result.ok is False
    assert result.code == "invalid_request"


def test_windows_diagnostics_returns_matching_software():
    capability = WindowsDiagnosticsCapability()

    fake_entries = [
        {
            "display_name": "Macrium Reflect Free",
            "display_version": "8.0.7783",
            "publisher": "Paramount Software (UK) Ltd.",
            "install_date": "20231220",
            "install_location": "",
            "uninstall_string": "MsiExec.exe /I{TEST}",
            "registry_source": "HKLM-64",
            "registry_subkey": "{TEST}",
        },
        {
            "display_name": "Not Macrium",
            "display_version": "1.0",
            "publisher": "Example",
            "install_date": "",
            "install_location": "",
            "uninstall_string": "",
            "registry_source": "HKCU",
            "registry_subkey": "{OTHER}",
        },
    ]

    with patch.object(
        capability,
        "_read_location",
        return_value=fake_entries,
    ):
        result = capability.execute(
            {
                "operation": "software_lookup",
                "name": "Macrium",
            },
            CapabilityContext(
                permissions={"windows.diagnostics.read"},
            ),
        )

    assert result.ok is True
    assert result.code == "ok"
    assert result.data["operation"] == "software_lookup"
    assert result.data["query"] == "Macrium"
    assert result.data["match_count"] == 6
    assert result.data["matches"][0]["display_name"] == "Macrium Reflect Free"
