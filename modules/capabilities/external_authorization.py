from hashlib import sha256
from threading import Lock


class ExternalAuthorization:
    """One-shot authorization for a specific external capability request."""

    def __init__(self):
        self._authorized = set()
        self._lock = Lock()

    @staticmethod
    def _key(capability_name, request):
        normalized = repr(
            (
                capability_name,
                tuple(sorted(request.items())),
            )
        )
        return sha256(normalized.encode("utf-8")).hexdigest()

    def authorize(self, capability_name, request):
        key = self._key(capability_name, request)

        with self._lock:
            self._authorized.add(key)

        return True

    def consume(self, capability_name, request):
        key = self._key(capability_name, request)

        with self._lock:
            if key not in self._authorized:
                return False

            self._authorized.remove(key)
            return True
