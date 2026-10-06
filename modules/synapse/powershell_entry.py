import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synapse.client import SynapseClient


def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: powershell_entry.py <operation>"
        )

    operation = sys.argv[1]
    payload_text = os.environ.get("ZEBRALINK_PAYLOAD", "{}")

    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON payload: {exc}")

    if not isinstance(payload, dict):
        raise SystemExit("JSON payload must be an object")

    client = SynapseClient(
        "http://127.0.0.1:52336/development",
        os.environ["ZEBRABRAVO_DEVELOPMENT_TOKEN"],
    )

    result = client.request(
        operation,
        payload=payload,
        request_id="powershell-synapse",
    )

    print("=== ZEBRALINK RESPONSE ===")
    print("OK:", result.get("ok"))
    print("REQUEST:", result.get("request_id"))
    print("OPERATION:", result.get("operation"))

    if result.get("ok"):
        print("DATA:")
        print(result.get("data", ""))
    else:
        print("CODE:", result.get("code"))
        print("MESSAGE:", result.get("message"))

    print("=== END ZEBRALINK RESPONSE ===")


if __name__ == "__main__":
    main()
