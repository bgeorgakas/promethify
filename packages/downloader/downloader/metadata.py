from db.enum import ResourceType

class TrackMetadata:
    id: str

    artist: str
    album: str
    disc_number: int
    name: str
    year: int
    cover_hex_id: str

    def __init__(self, id: str, artist: str, album: str, disc_number: int, name: str, year: int, cover_hex_id: str) -> None:
        self.id = id
        self.artist = artist
        self.album = album
        self.disc_number = disc_number
        self.name = name
        self.year = year
        self.cover_hex_id = cover_hex_id

    def __str__(self) -> str:
        return f"{self.artist} - {self.album} - Disc {self.disc_number} - {self.name}"
    
    def to_path(self, ext: str = '.ogg') -> str:
        return f"{self.artist}/{self.album}/Disc {self.disc_number}/{self.name}{ext}"
    

    
class ResourceMetadata:
    id: str
    resource_type: ResourceType
    name: str
    tracks: list[TrackMetadata]

    def __init__(self, id: str, resource_type: ResourceType, name: str, tracks: list[TrackMetadata]) -> None:
        self.id = id
        self.resource_type = resource_type
        self.name = name
        self.tracks = tracks

    def __str__(self) -> str:
        return f"{self.resource_type.value.capitalize()}\n{self.name}\nTracks:\n" + "\n".join([f"  {track}" for track in self.tracks])
    