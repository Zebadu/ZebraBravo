from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.context import CapabilityContext
from capabilities.plugins.test import TestCapability
from types import SimpleNamespace
from unittest.mock import patch


def test_test_capability_returns_structured_verification_summary(tmp_path):
    capability = TestCapability()

    context = CapabilityContext(
        workspace_root=tmp_path,
        permissions=frozenset({"test.run"}),
    )

    completed = SimpleNamespace(
        returncode=0,
        stdout="35 passed in 0.37s",
        stderr="",
    )

    verification = {
        "tests_total": 35,
        "tests_passed": 35,
        "tests_failed": 0,
        "tests_errors": 0,
        "tests_skipped": 0,
    }

    with patch(
        "capabilities.plugins.test.subprocess.run",
        return_value=completed,
    ):
        with patch(
            "capabilities.plugins.test.TestCapability._read_verification_report",
            return_value=verification,
        ):
            result = capability.execute(
                {"operation": "pytest"},
                context,
            )

    assert result.ok is True
    assert result.data["verification"] == verification
