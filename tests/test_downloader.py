from downloader.auth import create_librespot_session
from downloader.core import get_resource_metadata, download_track
import os

def test_create_librespot_session():
    session = create_librespot_session(os.getenv("CREDENTIALS_PATH"), is_auth=False)
    assert session is not None

def test_get_resource_metadata():
    session = create_librespot_session(os.getenv("CREDENTIALS_PATH"), is_auth=False)
    resource_metadata = get_resource_metadata('3n3Ppam7vgaVa1iaRUc9Lp', 'track', session)
    assert resource_metadata is not None
    print(resource_metadata)

def test_download_track():
    session = create_librespot_session()
    track_metadata = download_track('00TFDHSe7s8cWm5CzDY8UP', session)
    assert track_metadata is not None
    print(track_metadata)
