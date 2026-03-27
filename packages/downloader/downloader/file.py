import os
from zipfile import ZipFile
import boto3
from mypy_boto3_s3 import S3Client

from downloader.metadata import ResourceMetadata, TrackMetadata

def zip_resource(resource: ResourceMetadata, music_path: str, archive_path: str) -> str:
    
    output_path = os.path.join(archive_path, f"{resource.id}.zip")
    if os.path.exists(output_path):
        print(f"Archive already exists for resource {resource.id}, skipping zipping.")
        return output_path
    
    print(f"Zipping resource {resource.id} with {len(resource.tracks)} tracks to {output_path}")
    os.makedirs(archive_path, exist_ok=True)
    with ZipFile(output_path, 'w') as zipf:
        for track in resource.tracks:
            track_path = os.path.join(music_path, track.to_path())

            if resource.resource_type == 'playlist':
                track_zip_path = os.path.join(resource.name, track.name + '.ogg')

            else:
                track_zip_path = track.to_path()


            try:
                zipf.write(track_path, track_zip_path)
            except FileNotFoundError:
                print(f"Track file not found: {track_path}")
            except Exception as e:
                print(f"Error zipping track {track.name}: {e}")

    return output_path

class Uploader:
    endpoint_url: str
    access_key_id: str
    secret_access_key: str
    s3_client: S3Client
    bucket_name: str = "promethify"

    def __init__(self):
        self.endpoint_url = os.getenv("ENDPOINT_URL")
        if not self.endpoint_url:
            raise ValueError("ENDPOINT_URL environment variable is not set.")
        
        self.access_key_id = os.getenv("ACCESS_KEY_ID")
        if not self.access_key_id:
            raise ValueError("ACCESS_KEY_ID environment variable is not set.")
        
        self.secret_access_key = os.getenv("SECRET_ACCESS_KEY")
        if not self.secret_access_key:
            raise ValueError("SECRET_ACCESS_KEY environment variable is not set.")
        
        self.s3_client = boto3.client(
            service_name = 's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name='auto'
        )

    def object_exists(self, bucket_name: str, object_key: str) -> bool:
        
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=object_key)
            return True
        
        except self.s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    def generate_url(self, object_key: str) -> str:
        return self.s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': self.bucket_name, 'Key': object_key},
            ExpiresIn=3600
        )
    
    def upload_file(self, file_path: str) -> str:
        file_name = os.path.basename(file_path)
        
        if self.object_exists(self.bucket_name, file_name):
            print(f"File {file_name} already exists in bucket, skipping upload.")
            return self.generate_url(file_name)
        
        print(f"Uploading file {file_name} to bucket")
        try:
            self.s3_client.upload_file(
                Filename=file_path, Bucket=self.bucket_name, Key=file_name)
            return self.generate_url(file_name)
        
        except Exception as e:
            print(f"Error uploading file {file_name}: {e}")
            raise