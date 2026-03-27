from librespot import metadata
from urllib.parse import urlparse

def parse_spotify_url(url: str) -> tuple[str, str]:

    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) >= 2 and path_parts[0] in ['track', 'album', 'playlist']:
        return path_parts[0], path_parts[1]
    
    raise ValueError("Invalid Spotify URL")

def parse_spotify_uri(uri: str) -> tuple[str, str]:

    if uri.startswith("spotify:"):
        parts = uri.split(':')
        if len(parts) >= 3 and parts[1] in ['track', 'album', 'playlist']:
            return parts[1], parts[2]
    
    raise ValueError("Invalid Spotify URI")


_base62 = metadata.Base62.create_instance_with_inverted_character_set()
def gid_to_base62(gid: bytes) -> str:
    return _base62.encode(gid, 22).decode()

def get_cover_url(hex_id: str) -> str:
    return f"https://i.scdn.co/image/{hex_id}"