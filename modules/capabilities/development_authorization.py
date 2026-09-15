class DevelopmentAuthorization:
    """Mutable session authorization for governed development work."""

    def __init__(self, enabled=False):
        self._enabled = bool(enabled)

    @property
    def enabled(self):
        return self._enabled

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False
