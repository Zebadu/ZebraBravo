class ZoeyContinuityService:
    def __init__(self, repository):
        self.repository = repository

    def get_current(self):
        continuity = self.repository.load()
        return continuity["zoey"]