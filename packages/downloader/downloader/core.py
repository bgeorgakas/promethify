import os
import time

from librespot.core import Session
from librespot import metadata
from librespot.audio.decoders import VorbisOnlyAudioQuality, AudioQuality
import music_tag

from downloader import auth, utils, file
from downloader.metadata import ResourceMetadata, TrackMetadata
import db
from db.enum import JobStatus, ResourceType





DB_POLL_INTERVAL = 5

class Downloader:
    session: Session
    music_path: str
    archive_path: str
    credentials_path: str
    archive_path: str
    uploader: file.Uploader

    def __init__(self) -> None:

        self.credentials_path = os.getenv("CREDENTIALS_PATH")
        if not self.credentials_path:
            raise ValueError("CREDENTIALS_PATH not set in environment variables")
        
        library_path = os.getenv("LIBRARY_PATH")
        if not library_path:
            raise ValueError("LIBRARY_PATH not set in environment variables")
        
        self.music_path = os.path.join(library_path, "music")
        self.archive_path = os.path.join(library_path, "archive")

        self.session = auth.create_librespot_session(self.credentials_path)

        self.uploader = file.Uploader()


    def _download_cover(self, cover_hex_id: str, cover_path: str) -> None:
        if os.path.exists(cover_path):
            print(f"Cover already exists at {cover_path}, skipping download")
            return
        
        print(f"Downloading cover with hex ID: {cover_hex_id}")
        try:
            response = self.session.client().get(utils.get_cover_url(cover_hex_id))
            response.raise_for_status()
            with open(cover_path, 'wb') as f:
                f.write(response.content)

        except Exception as e:
            print(f"Failed downloading cover with hex ID: {cover_hex_id}, error: {e}")


    def _write_track_metadata(self, track: TrackMetadata, track_path: str, cover_path: str) -> None:

        try:
            file = music_tag.load_file(track_path)
            file['artist'] = track.artist
            file['album'] = track.album
            file['name'] = track.name
            file['disc_number'] = str(track.disc_number)
            file['year'] = str(track.year)

            with open(cover_path, 'rb') as f:
                file['artwork'] = f.read()
            
            file.save()
            
        except Exception as e:
            print(f"Failed tagging track: {track}, error: {e}")


    def _download_track(self, track_id: str, ext = '.ogg') -> TrackMetadata | None:

        try:
            track_metadata = self.session.api().get_metadata_4_track(metadata.TrackId.from_base62(track_id))

        except Exception as e:
            print(f"Failed getting track metadata for track ID: {track_id}, error: {e}")
            return None

        track = TrackMetadata(
            id=track_id,
            artist=track_metadata.artist[0].name,
            album=track_metadata.album.name,
            disc_number=track_metadata.disc_number,
            name=track_metadata.name,
            year=track_metadata.album.date.year,
            cover_hex_id = track_metadata.album.cover_group.image[0].file_id.hex()
        )
  
        track_path = os.path.join(self.music_path, track.to_path(ext))
        track_dir = os.path.dirname(track_path)
        cover_path = os.path.join(track_dir, 'cover.jpg')
        

        if os.path.exists(track_path):
            print(f"Track already exists at {track_path}, skipping download")
            return track
        
        
        print(f"Downloading track: {track}")
        os.makedirs(track_dir, exist_ok=True)

        try:
            stream = self.session.content_feeder().load(
                metadata.TrackId.from_base62(track.id), 
                VorbisOnlyAudioQuality(AudioQuality.VERY_HIGH),
                False, None
            )

            inner = stream.input_stream.stream()
            total_size = inner.size()

            with open(track_path, 'wb') as f:
                while inner.pos() < total_size:
                    to_read = min(1024, total_size - inner.pos())
                    chunk = inner.read(to_read)
                    if not chunk:
                        break
                    f.write(chunk)
            
        except Exception as e:
            print(f"Failed downloading track: {track}, error: {e}")
            return None
        

        self._download_cover(track.cover_hex_id, cover_path)
        self._write_track_metadata(track, track_path, cover_path)
        
        return track

    def download_resource(self, resource_id: str, resource_type: ResourceType) -> ResourceMetadata:

        name: str
        track_ids = []

        if resource_type == ResourceType.TRACK:
            try:
                track_metadata = self.session.api().get_metadata_4_track(metadata.TrackId.from_base62(resource_id))
                name = track_metadata.name
                track_ids = [utils.gid_to_base62(track_metadata.gid)]
                

            except Exception as e:
                print(f"Failed getting track metadata for track ID: {resource_id}")
                raise

            

        elif resource_type == ResourceType.ALBUM:
            try:
                album_metadata = self.session.api().get_metadata_4_album(metadata.AlbumId.from_base62(resource_id))
            except Exception as e:
                print(f"Failed getting album metadata for album ID: {resource_id}")
                raise
            
            name = album_metadata.name
            for disc in album_metadata.disc:
                for track in disc.track:
                    track_ids.append(utils.gid_to_base62(track.gid))
            
            

        elif resource_type == ResourceType.PLAYLIST:
            try:
                playlist_metadata = self.session.api().get_playlist(metadata.PlaylistId(resource_id))
            except Exception as e:
                print(f"Failed getting playlist metadata for playlist ID: {resource_id}")
                raise
            
            name = playlist_metadata.attributes.name
            for track in playlist_metadata.contents.items:
                track_ids.append(utils.parse_spotify_uri(track.uri)[1])
                    
        

        tracks = [self._download_track(track_id) for track_id in track_ids]
            
        return ResourceMetadata(
            id=resource_id,
            resource_type=resource_type,
            name=name,
            tracks=tracks
        )
    


    def start(self, exit_after: bool = False) -> None:
        while True:
            job = db.core.get_pending_job()

            if job is None:
                if exit_after:
                    print("No pending jobs, exiting...")
                    break
                
                print("No pending jobs, sleeping...")
                time.sleep(DB_POLL_INTERVAL)
                continue
            
            print(f"Running job: {job.id}")

            try:
                resource = self.download_resource(job.resource_id, job.resource_type)
                
                if None in resource.tracks:
                    num_failed_tracks = sum(track is None for track in resource.tracks)
                    error_message = f"Failed to download {num_failed_tracks} of {len(resource.tracks)} tracks."
                    print(error_message)
                    db.core.update_job(job.id, error_message=error_message)

                output_path = file.zip_resource(resource, self.music_path, self.archive_path)
                download_url = self.uploader.upload_file(output_path)

                db.core.update_job(job.id, download_url = download_url, status=db.models.JobStatus.COMPLETED)

            except Exception as e:
                print(f"Failed processing job {job.id} for resource {job.resource_id}, error: {e}")
                db.core.update_job(job.id, error_message=str(e), status=db.models.JobStatus.FAILED)

