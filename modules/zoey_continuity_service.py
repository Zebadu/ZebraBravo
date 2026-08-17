class ZoeyContinuityService:
    ALLOWED_FIELDS = {
        "status",
        "personality",
        "future_domains",
    }

    def __init__(self, repository):
        self.repository = repository

    def get_current(self):
        continuity = self.repository.load()
        return continuity["zoey"]

    def update_field(self, field, value):
        if field not in self.ALLOWED_FIELDS:
            raise ValueError(
                f"Unknown Zoey continuity field: {field}"
            )

        continuity = self.repository.load()
        continuity["zoey"][field] = value
        self.repository.save(continuity)

    def get_personality(self):
        zoey = self.get_current()
        return zoey["personality"]

    def update_personality_trait(self, trait):
        if not isinstance(trait, str):
            raise ValueError("Zoey personality trait must be a string.")

        trait = trait.strip()

        if not trait:
            raise ValueError("Zoey personality trait cannot be empty.")

        continuity = self.repository.load()
        personality = continuity["zoey"]["personality"]
        traits = personality["traits"]

        if trait not in traits:
            traits.append(trait)

        self.repository.save(continuity)