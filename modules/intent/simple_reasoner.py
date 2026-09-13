import re
from typing import Any, Mapping


class SimpleIntentReasoner:
    """Deterministic natural-language reasoner for initial application integration."""

    def reason(self, request: str) -> Mapping[str, Any]:
        text = request.strip()

        if not text:
            raise ValueError("Request cannot be empty.")

        match = re.search(
            r"(?:show|read|open|display)\s+(?:me\s+)?(?:the\s+)?(.+)",
            text,
            re.IGNORECASE,
        )

        if match:
            path = match.group(1).strip().rstrip("?.!")

            return {
                "name": "read_file",
                "capability": "filesystem",
                "operation": "read",
                "parameters": {"path": path},
                "route": "capability",
            }

        raise ValueError(
            f"Unable to determine intent for request: {request}"
        )
