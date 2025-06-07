from app.memory.short_term_memory import ShortTermMemory

class FaissCore:
    def __init__(self):
        self.memory = ShortTermMemory()

    def get_recent(self, limit=10):
        return self.memory.texts[-limit:]