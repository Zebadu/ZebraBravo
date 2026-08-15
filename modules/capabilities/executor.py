from capabilities.contracts import (
    CapabilityError,
    CapabilityPermissionDenied,
    CapabilityResult,
    InvalidCapabilityRequest,
)


class CapabilityExecutor:
    def __init__(self, registry):
        self.registry = registry

    def execute(self, capability_name, request, context):
        capability = self.registry.get(capability_name)

        if capability is None:
            return CapabilityResult(
                ok=False,
                message=f"Capability not found: {capability_name}",
                code="capability_not_found",
            )

        if not capability.metadata.required_permissions.issubset(context.permissions):
            return CapabilityResult(
                ok=False,
                message="Capability permission denied.",
                code="permission_denied",
            )

        try:
            result = capability.execute(request, context)

            if not isinstance(result, CapabilityResult):
                return CapabilityResult(
                    ok=False,
                    message="Capability returned an invalid result.",
                    code="execution_failed",
                )

            return result

        except InvalidCapabilityRequest as error:
            return CapabilityResult(
                ok=False,
                data=error.data,
                message=error.message,
                code=error.code,
            )

        except CapabilityPermissionDenied as error:
            return CapabilityResult(
                ok=False,
                data=error.data,
                message=error.message,
                code=error.code,
            )

        except CapabilityError as error:
            return CapabilityResult(
                ok=False,
                data=error.data,
                message=error.message,
                code=error.code,
            )

        except Exception:
            return CapabilityResult(
                ok=False,
                message="Capability execution failed.",
                code="execution_failed",
            )
