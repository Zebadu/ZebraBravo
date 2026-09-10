from capabilities.contracts import CapabilityResult
from capabilities.runtime import CapabilityRuntime


class IntentExecutor:
    """Execute validated intents through the controlled capability runtime."""

    def __init__(self, runtime: CapabilityRuntime):
        self.runtime = runtime

    def execute(self, intent):
        if intent.route == "development":
            request = {
                "operation": intent.operation,
                "payload": dict(intent.parameters),
            }

            response = self.runtime.execute_development(request)

            if isinstance(response, CapabilityResult):
                return response

            return CapabilityResult(
                ok=response.get("ok", False),
                data=response.get("data"),
                message=response.get("message", ""),
                code=response.get("code", "unknown"),
            )

        request = {
            "operation": intent.operation,
            **intent.parameters,
        }

        return self.runtime.execute(
            intent.capability,
            request,
        )