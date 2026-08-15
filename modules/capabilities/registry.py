class CapabilityRegistry:
    def __init__(self):
        self._capabilities = {}

    def register(self, capability):
        name = capability.metadata.name

        if name in self._capabilities:
            raise ValueError(f"Capability already registered: {name}")

        self._capabilities[name] = capability

    def get(self, name):
        return self._capabilities.get(name)

    def names(self):
        return tuple(sorted(self._capabilities))
