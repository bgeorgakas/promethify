from pydantic import BaseModel, ConfigDict
from datetime import datetime
from db.enum import JobStatus, ResourceType

class Job(BaseModel):
    id: str
    resource_id: str
    resource_type: ResourceType
    download_url: str | None
    created_at: datetime
    status: JobStatus
    error_message: str | None

    model_config = ConfigDict(
        from_attributes=True
    )