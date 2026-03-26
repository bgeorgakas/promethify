import os
from urllib.parse import urlparse

from librespot.core import Session
from librespot import metadata
from librespot.audio.decoders import VorbisOnlyAudioQuality, AudioQuality

from downloader import auth, utils


class TrackMetadata:
    id: str

    artist: str
    album: str
    disc_number: int
    title: str
    year: int

    def __init__(self, id: str, artist: str, album: str, disc_number: int, title: str, year: int) -> None:
        self.id = id
        self.artist = artist
        self.album = album
        self.disc_number = disc_number
        self.title = title
        self.year = year

    def __str__(self) -> str:
        return f"{self.artist} - {self.album} - Disc {self.disc_number} - {self.title}"
    
    def to_path(self, ext: str = '.ogg') -> str:
        return f"{self.artist}/{self.album}/Disc {self.disc_number}/{self.title}{ext}"
    

    
class ResourceMetadata:
    id: str
    resource_type: str
    name: str

    tracks: list[TrackMetadata]

    def __init__(self, id: str, resource_type: str, name: str, tracks: list[TrackMetadata]) -> None:
        self.id = id
        self.resource_type = resource_type
        self.name = name
        self.tracks = tracks

    def __str__(self) -> str:
        return f"{self.resource_type.capitalize()}\n{self.name}\nTracks:\n" + "\n".join([f"  {track}" for track in self.tracks])
    
def get_resource_metadata(resource_id: str, resource_type: str, session: Session) -> ResourceMetadata:

    name: str

    if resource_type == 'track':
        track_metadata = session.api().get_metadata_4_track(metadata.TrackId.from_base62(resource_id))
        track_ids = [utils.gid_to_base62(track_metadata.gid)]
        name = track_metadata.name

    elif resource_type == 'album':
        album_metadata = session.api().get_metadata_4_album(metadata.AlbumId.from_base62(resource_id))
        track_ids = [
            utils.gid_to_base62(track.gid)
            for disc in album_metadata.disc
            for track in disc.track  
        ]
        name = album_metadata.name

    elif resource_type == 'playlist':
        resource_metadata = session.api().get_metadata_4_playlist(metadata.PlaylistId(resource_id))
        track_ids = [
            utils.parse_spotify_uri(track.uri)[1]
            for track in resource_metadata.contents.items
        ]
        name = resource_metadata.attributes.name

    tracks = []
    for track_id in track_ids:
        track_metadata = session.api().get_metadata_4_track(metadata.TrackId.from_base62(track_id))
        tracks.append(TrackMetadata(
            id=track_id,
            artist=track_metadata.artist[0].name,
            album=track_metadata.album.name,
            disc_number=track_metadata.disc_number,
            title=track_metadata.name,
            year=track_metadata.album.date.year
        ))

    return ResourceMetadata(
        id=resource_id,
        resource_type=resource_type,
        name=name,
        tracks=tracks
    )

def download_track(track: TrackMetadata, session: Session, library_path: str, ext = '.ogg') -> bool:

    output_path = os.path.join(library_path, track.to_path(ext))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)


    stream = session.content_feeder().load(
        metadata.TrackId.from_base62(track.id), 
        VorbisOnlyAudioQuality(AudioQuality.VERY_HIGH),
        False, None
    )

    with open(output_path, 'wb') as f:
        chunk = None
        while chunk != b'':
            chunk = stream.input_stream.stream().read(1024)
            f.write(chunk)

    return True


class Downloader:
    session: Session
    library_path: str
    credentials_path: str

    def __init__(self) -> None:

        self.credentials_path = os.getenv("CREDENTIALS_PATH")
        if not self.credentials_path:
            raise ValueError("CREDENTIALS_PATH not set in environment variables")
        
        self.library_path = os.getenv("LIBRARY_PATH")
        if not self.library_path:
            raise ValueError("LIBRARY_PATH not set in environment variables")
        
        self.session = auth.create_librespot_session(self.credentials_path)

    def start(self) -> None:
        pass
