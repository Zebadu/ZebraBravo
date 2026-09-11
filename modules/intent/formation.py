from .contracts import Intent


class IntentFormation:
    """Create validated Intent objects from structured intent information."""

    def form(
        self,
        name,
        capability,
        operation,
        parameters=None,
        route="capability",
    ):
        return Intent(
            name=name,
            capability=capability,
            operation=operation,
            parameters={} if parameters is None else parameters,
            route=route,
        )
