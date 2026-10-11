import base64
import ipaddress
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from capabilities.visual_observation import VisualObservation


class QwenWorkerClient:
    """Lightweight VisionProvider adapter for a local Qwen inference worker."""

    MAX_IMAGE_BYTES = 8 * 1024 * 1024
    MAX_RESPONSE_BYTES = 64 * 1024

    def __init__(self, url=None, auth_token=None, timeout=90):
        self.url = url or os.environ.get(
            "ZEBRABRAVO_VISION_URL",
            "http://127.0.0.1:52337/describe",
        )
        self.auth_token = auth_token or os.environ.get(
            "ZEBRABRAVO_VISION_TOKEN",
            "",
        )
        self.timeout = timeout

        parsed = urlsplit(self.url)
        if (
            parsed.scheme != "http"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("Vision worker URL must be a plain local HTTP endpoint.")

        hostname = parsed.hostname.lower()
        is_loopback = hostname == "localhost"
        if not is_loopback:
            try:
                is_loopback = ipaddress.ip_address(hostname).is_loopback
            except ValueError:
                is_loopback = False

        if not is_loopback:
            raise ValueError("Vision worker must use a loopback address.")

        if not parsed.path or not self.auth_token:
            raise ValueError("Vision worker endpoint and authentication token are required.")

        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValueError("Timeout must be positive.")

    def describe(self, observation: VisualObservation) -> str:
        if not isinstance(observation, VisualObservation):
            raise TypeError("A VisualObservation is required.")

        if not observation.data:
            raise ValueError("Observation image data is empty.")

        if len(observation.data) > self.MAX_IMAGE_BYTES:
            raise ValueError("Observation exceeds the image payload limit.")

        payload = {
            "observation_id": observation.observation_id,
            "source": observation.source,
            "title": observation.title,
            "width": observation.width,
            "height": observation.height,
            "format": observation.format,
            "captured_at": observation.captured_at,
            "provenance": observation.provenance,
            "image_base64": base64.b64encode(observation.data).decode("ascii"),
        }

        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        request = Request(
            self.url,
            data=body,
            headers={
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                length = response.headers.get("Content-Length")
                if length is not None and int(length) > self.MAX_RESPONSE_BYTES:
                    raise RuntimeError("Vision worker response exceeds the size limit.")
                raw = response.read(self.MAX_RESPONSE_BYTES + 1)

            if len(raw) > self.MAX_RESPONSE_BYTES:
                raise RuntimeError("Vision worker response exceeds the size limit.")

            result = json.loads(raw.decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(
                f"Vision worker rejected the request (HTTP {exc.code})."
            ) from None
        except (URLError, TimeoutError, OSError) as exc:
            raise RuntimeError("Vision worker is unavailable.") from exc
        except (ValueError, UnicodeDecodeError) as exc:
            raise RuntimeError("Vision worker returned an invalid response.") from exc

        if not isinstance(result, dict) or result.get("ok") is not True:
            raise RuntimeError("Vision worker did not complete the request.")

        description = result.get("description")
        if not isinstance(description, str) or not description.strip():
            raise RuntimeError("Vision worker returned no valid description.")

        return description.strip()
