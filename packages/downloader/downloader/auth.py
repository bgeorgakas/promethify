import os
import time
from librespot.core import Session

def create_librespot_session(credentials_path: str, is_auth: bool = True, retry = True) -> Session:

    if os.path.exists(credentials_path):
        print(f"Using credentials from {credentials_path}")
        try:
            return Session.Builder().stored_file(credentials_path).create()
        
        except Exception as e:
            if retry:
                print(f"Failed to create session with stored credentials: {e}. Retrying in 5 seconds...")
                time.sleep(5)
                return create_librespot_session(credentials_path, is_auth=is_auth, retry=False)
            else:
                raise
    
    elif is_auth:
        print(f"Credentials file not found at {credentials_path}. Starting OAuth flow.")
        def callback(url: str) -> None:
            print(f"Please open the following URL in your browser to authenticate: {url}")

        return Session.Builder(
            Session.Configuration.Builder().set_stored_credential_file(credentials_path).build()
        ).oauth(callback).create()
    
    else:
        raise ValueError("Credentials file not found and auth not enabled")
		