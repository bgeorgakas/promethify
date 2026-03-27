import db

def test_add_job():
    db.core.init_db()
    db.core.add_job("http://example.com/resource1")
    job_id, resource_url = db.core.get_pending_job()
    assert resource_url == "http://example.com/resource1"

    db.core.update_job(job_id, download_url="http://example.com/download1", status=db.models.JobStatus.COMPLETED)

    job_id, resource_url = db.core.get_pending_job()
    assert job_id is None