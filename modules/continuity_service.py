class ContinuityService:
    def __init__(self, repository):
        self.repository = repository

    def get_current(self):
        return self.repository.load()

    def update_next_action(self, next_action):
        continuity = self.repository.load()
        continuity["next_action"] = next_action
        self.repository.save(continuity)