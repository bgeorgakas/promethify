import os
import threading

import db
from downloader.auth import create_librespot_session
from downloader.core import Downloader

def test_downloader():
    db.core.init_db()
    job1_id = db.core.add_job("https://open.spotify.com/track/59e3tozWHknnpbh7m4SAkH?si=4e6eef4266e8435e")
    job2_id = db.core.add_job("https://open.spotify.com/playlist/1QE0TkAVFObb3bKzSwqyUZ?si=TuvuWoDoS16b9bAuwx-3Tg")
    job3_id = db.core.add_job("https://open.spotify.com/album/200xhXQBPc2OWPsZ3koxTc?si=q4-L0hV6TKKAgktgBAspVg")

    downloader = Downloader()

    thread = threading.Thread(target=downloader.start, kwargs={"exit_after": True})
    thread.start()

    thread.join()
    assert thread.is_alive() == False

    job_status = db.core.get_job_status(job1_id)
    assert job_status == db.models.JobStatus.COMPLETED
    job_status = db.core.get_job_status(job2_id)
    assert job_status == db.models.JobStatus.COMPLETED
    job_status = db.core.get_job_status(job3_id)
    assert job_status == db.models.JobStatus.COMPLETED
    