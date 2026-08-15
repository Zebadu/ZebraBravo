import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.context import CapabilityContext  # noqa: E402
from capabilities.contracts import (  # noqa: E402
    CapabilityError,
    CapabilityMetadata,
    CapabilityPermissionDenied,
    CapabilityResult,
    InvalidCapabilityRequest,
)
from capabilities.executor import CapabilityExecutor  # noqa: E402
from capabilities.registry import CapabilityRegistry  # noqa: E402


class FakeCapability:
    def __init__(self, name, handler, required_permissions=()):
        self.metadata = CapabilityMetadata(
            name=name,
            description=f"Fake {name} capability.",
            required_permissions=frozenset(required_permissions),
        )
        self.handler = handler

    def execute(self, request, context):
        return self.handler(request, context)


class CapabilityRegistryTests(unittest.TestCase):
    def test_registration_and_deterministic_lookup(self):
        registry = CapabilityRegistry()
        alpha = FakeCapability("alpha", lambda request, context: CapabilityResult(True))
        zebra = FakeCapability("zebra", lambda request, context: CapabilityResult(True))

        registry.register(zebra)
        registry.register(alpha)

        self.assertIs(registry.get("alpha"), alpha)
        self.assertIs(registry.get("zebra"), zebra)
        self.assertEqual(registry.names(), ("alpha", "zebra"))

    def test_duplicate_name_is_rejected(self):
        registry = CapabilityRegistry()
        registry.register(FakeCapability("echo", lambda request, context: CapabilityResult(True)))

        with self.assertRaisesRegex(ValueError, "Capability already registered: echo"):
            registry.register(FakeCapability("echo", lambda request, context: CapabilityResult(True)))

    def test_metadata_is_immutable(self):
        metadata = CapabilityMetadata("echo", "Echo input.")

        with self.assertRaises(Exception):
            metadata.name = "other"


class CapabilityExecutorTests(unittest.TestCase):
    def setUp(self):
        self.registry = CapabilityRegistry()
        self.executor = CapabilityExecutor(self.registry)
        self.context = CapabilityContext()

    def test_success(self):
        self.registry.register(
            FakeCapability("echo", lambda request, context: CapabilityResult(True, request["text"]))
        )

        result = self.executor.execute("echo", {"text": "hello"}, self.context)

        self.assertEqual(result, CapabilityResult(True, "hello"))

    def test_unknown_capability(self):
        result = self.executor.execute("missing", {}, self.context)

        self.assertEqual(result.ok, False)
        self.assertEqual(result.code, "capability_not_found")

    def test_invalid_request(self):
        def handler(request, context):
            raise InvalidCapabilityRequest("text is required")

        self.registry.register(FakeCapability("echo", handler))
        result = self.executor.execute("echo", {}, self.context)

        self.assertEqual(result.code, "invalid_request")
        self.assertEqual(result.message, "text is required")

    def test_denied_execution(self):
        self.registry.register(
            FakeCapability(
                "restricted",
                lambda request, context: CapabilityResult(True),
                required_permissions={"restricted.execute"},
            )
        )

        result = self.executor.execute("restricted", {}, self.context)

        self.assertEqual(result.code, "permission_denied")

    def test_capability_reported_permission_denial(self):
        def handler(request, context):
            raise CapabilityPermissionDenied("Operation denied by capability.")

        self.registry.register(FakeCapability("restricted", handler))
        result = self.executor.execute("restricted", {}, self.context)

        self.assertEqual(result.code, "permission_denied")
        self.assertEqual(result.message, "Operation denied by capability.")

    def test_known_failure(self):
        def handler(request, context):
            raise CapabilityError("operation_failed", "Operation could not complete.")

        self.registry.register(FakeCapability("known-failure", handler))
        result = self.executor.execute("known-failure", {}, self.context)

        self.assertEqual(result.code, "operation_failed")
        self.assertEqual(result.message, "Operation could not complete.")

    def test_unexpected_exception(self):
        def handler(request, context):
            raise RuntimeError("unexpected")

        self.registry.register(FakeCapability("broken", handler))
        result = self.executor.execute("broken", {}, self.context)

        self.assertEqual(result.code, "execution_failed")
        self.assertEqual(result.message, "Capability execution failed.")
