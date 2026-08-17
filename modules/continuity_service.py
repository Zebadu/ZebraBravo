class ContinuityService:
    def __init__(self, repository):
        self.repository = repository

    def get_current(self):
        return self.repository.load()

    def update_next_action(self, next_action):
        if not isinstance(next_action, str):
            raise ValueError(
                "Next action must be text."
            )

        continuity = self.repository.load()
        continuity["next_action"] = next_action
        self.repository.save(continuity)

    def update_checkpoint(self, checkpoint):
        if not isinstance(checkpoint, dict):
            raise ValueError(
                "Checkpoint must be an object."
            )

        continuity = self.repository.load()
        continuity["checkpoint"] = checkpoint
        self.repository.save(continuity)