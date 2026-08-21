from capabilities.runtime import CapabilityRuntime


class IntentExecutor:
    """Execute validated intents through the controlled capability runtime."""

    def __init__(self, runtime: CapabilityRuntime):
        self.runtime = runtime

    def execute(self, intent):
        request = {
            "operation": intent.operation,
            **intent.parameters,
        }

        return self.runtime.execute(
            intent.capability,
            request,
        )