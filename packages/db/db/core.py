import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session

from db import models, schemas


_engine = None

def _get_engine():
    global _engine

    application_name = os.getenv("APPLICATION_NAME")

    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        raise ValueError("POSTGRES_URL environment variable is not set")

    if _engine is None:
        connect_args = {"application_name": application_name} if application_name else {}
        _engine = create_engine(postgres_url, connect_args=connect_args)
    return _engine


def get_session() -> Session:
    return Session(bind=_get_engine())


def init_db():
    print("Initializing database...")

    meta = MetaData()
    meta.reflect(bind=_get_engine())
    meta.drop_all(bind=_get_engine())
    models.Base.metadata.create_all(_get_engine())



def add_job(resource_url: str) -> str:
    with get_session() as session:
        job = models.Job.from_resource_url(resource_url)
        session.add(job)
        session.commit()
        return job.id
    
def get_job_status(job_id: str) -> models.JobStatus | None:
    with get_session() as session:
        job = session.get(models.Job, job_id)
        if job:
            return job.status
    return None

def get_pending_job() -> schemas.Job | None:
    with get_session() as session:
        job = session.query(models.Job).filter(models.Job.status == models.JobStatus.PENDING).first()

        if job:
            job.status = models.JobStatus.RUNNING
            session.commit()
            return schemas.Job.model_validate(job)
        
    return None

def update_job(job_id: str, download_url: str | None = None, error_message: str | None = None, status: models.JobStatus | None = None):
    with get_session() as session:
        job = session.get(models.Job, job_id)

        if not job:
            raise ValueError(f"Job with id {job_id} not found")

        if download_url is not None:
            job.download_url = download_url
        if error_message is not None:
            job.error_message = error_message
        if status is not None:
            job.status = status

        session.commit()