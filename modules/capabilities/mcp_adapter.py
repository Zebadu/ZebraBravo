import json
from collections.abc import Mapping


class McpDevelopmentAdapter:
    """Expose read-only ZebraBravo development operations as MCP tools.

    This class deliberately contains no filesystem or capability logic.  Every
    tool call is translated into the existing DevelopmentProtocol, which keeps
    permissions and the Policy Gate authoritative.
    """

    PROTOCOL_VERSION = "2025-06-18"

    _TOOLS = {
        "project_info": {
            "description": "Return governed ZebraBravo project metadata.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        "list": {
            "description": "List a directory within the governed workspace.",
            "inputSchema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
            },
        },
        "read": {
            "description": "Read a file within the governed workspace.",
            "inputSchema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
        "search": {
            "description": "Search text within the governed workspace.",
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        "git_status": {
            "description": "Return governed Git status.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        "git_log": {
            "description": "Return governed Git log entries.",
            "inputSchema": {
                "type": "object",
                "properties": {"limit": {"type": "integer", "minimum": 1}},
            },
        },
        "git_diff": {
            "description": "Return the governed working-tree diff.",
            "inputSchema": {"type": "object", "properties": {}},
        },
    }

    def __init__(self, protocol):
        if protocol is None or not hasattr(protocol, "handle"):
            raise TypeError("An MCP adapter requires a development protocol.")

        self.protocol = protocol

    def handle(self, request):
        """Handle one JSON-RPC request without bypassing DevelopmentProtocol."""

        if not isinstance(request, Mapping):
            return self._error(None, -32600, "Request must be an object.")

        request_id = request.get("id")
        method = request.get("method")

        if not isinstance(method, str):
            return self._error(request_id, -32600, "Method is required.")

        if method == "initialize":
            return self._result(
                request_id,
                {
                    "protocolVersion": self.PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {
                        "name": "zebrabravo-development",
                        "version": "0.1",
                    },
                },
            )

        if method == "tools/list":
            return self._result(
                request_id,
                {
                    "tools": [
                        {"name": name, **definition}
                        for name, definition in self._TOOLS.items()
                    ]
                },
            )

        if method == "tools/call":
            return self._call_tool(request_id, request.get("params", {}))

        if method == "notifications/initialized":
            return None

        return self._error(request_id, -32601, "Method not found.")

    def _call_tool(self, request_id, params):
        if not isinstance(params, Mapping):
            return self._error(request_id, -32602, "Tool parameters must be an object.")

        name = params.get("name")
        arguments = params.get("arguments", {})

        if name not in self._TOOLS:
            return self._error(request_id, -32602, "Unknown or disallowed tool.")

        if not isinstance(arguments, Mapping):
            return self._error(request_id, -32602, "Tool arguments must be an object.")

        response = self.protocol.handle(
            {
                "request_id": str(request_id) if request_id is not None else None,
                "operation": name,
                "payload": dict(arguments),
            }
        )

        return self._result(
            request_id,
            {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(response, ensure_ascii=False),
                    }
                ],
                "structuredContent": response,
                "isError": not response["ok"],
            },
        )

    @staticmethod
    def _result(request_id, result):
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    @staticmethod
    def _error(request_id, code, message):
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        }
