from enum import Enum

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ResourceType(Enum):
    TRACK = "track"
    ALBUM = "album"
    PLAYLIST = "playlist"