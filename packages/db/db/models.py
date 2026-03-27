import enum
from uuid import uuid4
from datetime import datetime
from urllib.parse import urlparse

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime
import sqlalchemy

from db.enum import JobStatus, ResourceType

class Base(DeclarativeBase):
    pass



class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    resource_id: Mapped[str] = mapped_column(String, nullable = False)
    resource_type: Mapped[ResourceType] = mapped_column('resource_type', sqlalchemy.Enum(ResourceType), nullable = False)
    download_url: Mapped[str] = mapped_column(String, nullable = True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    status: Mapped[JobStatus] = mapped_column('status', sqlalchemy.Enum(JobStatus), default=JobStatus.PENDING)
    error_message: Mapped[str] = mapped_column(String, nullable = True)

    def __str__(self):
        return f"{self.resource_id}, {self.resource_type}, {self.download_url}, {self.created_at}, {self.status})"
    
    @staticmethod
    def from_resource_url(url: str) -> 'Job':
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[0] in ['track', 'album', 'playlist']:
            return Job(resource_id=path_parts[1], resource_type=ResourceType(path_parts[0]))
        
        raise ValueError("Invalid Spotify URL")