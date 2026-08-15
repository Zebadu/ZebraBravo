from capabilities.contracts import CapabilityResult


class PolicyCapabilityGateway:
    def __init__(self, registry, executor, policy):
        self.registry = registry
        self.executor = executor
        self.policy = policy

    def execute(self, capability_name, request, context):
        capability = self.registry.get(capability_name)

        if capability is None:
            return self.executor.execute(capability_name, request, context)

        decision = self.policy.evaluate(capability.metadata, request, context)

        if not decision.allowed:
            return CapabilityResult(
                ok=False,
                data=decision.data,
                message=decision.message,
                code=decision.code,
            )

        return self.executor.execute(capability_name, request, context)
