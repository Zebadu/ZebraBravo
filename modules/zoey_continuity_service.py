class ZoeyContinuityService:
    def __init__(self, repository):
        self.repository = repository

    def get_current(self):
        continuity = self.repository.load()
        return continuity["zoey"]

    def update_field(self, field, value):
        continuity = self.repository.load()

        if field not in continuity["zoey"]:
            raise ValueError(
                f"Unknown Zoey continuity field: {field}"
            )

        continuity["zoey"][field] = value
        self.repository.save(continuity)