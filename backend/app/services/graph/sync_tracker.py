from datetime import datetime

class SyncTracker:
    last_sync = None

    @classmethod
    def update(cls):
        cls.last_sync = datetime.utcnow()

    @classmethod
    def get(cls):
        return cls.last_sync
