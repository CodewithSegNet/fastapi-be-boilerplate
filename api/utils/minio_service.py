from datetime import timedelta
import json, requests, os
from uuid import uuid4
from minio import Minio
from minio.error import S3Error

from api.utils.settings import settings
from api.utils.mime_types import mime_types


class MinioService:

    def __init__(self):
        self.minio_client = Minio(
            endpoint='media.tifi.tv',
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=True
        )

    
    def __make_public(self, bucket_name: str):
        """This function makes a bucket public"""

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                }
            ]
        }
        
        # Set bucket policy
        self.minio_client.set_bucket_policy(bucket_name, json.dumps(policy))

    
    def generate_presigned_url(
        self, 
        object_name: str, 
        response_content_disposition: str = None
    ):
        bucket_name = 'tifi'
        try:
            url = self.minio_client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                response_headers={
                    "response-content-disposition": response_content_disposition
                } if response_content_disposition else None
            )
            return url
        except S3Error as s3_error:
            print(f'An error occured: {s3_error}')

    
    def upload_to_minio(
        self, 
        folder_name: str, 
        source_file: str, 
        destination_file: str = str(uuid4().hex),
        content_type: str = 'application/octet-stream'
    ):
        """This function saves a file to a minio bucket

        Args:
            folder_name (str): Name of the bucket to save the file to
            source_file (str): File path to the file to be save to minio bucket
            destination_file (str): Path to where the file should be saved in minio bucket
        """

        # file_extension = source_file.split('.')[-1]
        # content_type = mime_types[file_extension]
        bucket_name = 'tifi'
        destination = f"{folder_name}/{destination_file}"

        try:
            if not self.minio_client.bucket_exists(bucket_name):
                self.minio_client.make_bucket(bucket_name)
            
            self.__make_public(bucket_name)

            # Upload file
            self.minio_client.fput_object(
                bucket_name=bucket_name,
                object_name=destination,
                file_path=source_file,
                content_type=content_type
            )

            preview_url = self.generate_presigned_url(
                object_name=destination,
                response_content_disposition="inline"
            ).split('?')[0]

            # Generate download URL (attachment content disposition)
            download_url = self.generate_presigned_url(
                object_name=destination,
                response_content_disposition=f"attachment; filename={destination}"
            )

            return preview_url, download_url

        except S3Error as s3_error:
            print(f'An error occured: {s3_error}')

    
    def upload_to_tmp_bucket(
        self,
        source_file: str,
        # content_type: str = 'application/octet-stream'
    ):
        '''This function uploads a file to temporary bucket in minio'''

        bucket_name = 'tifi'
        file_extension = source_file.split('.')[-1]
        content_type = mime_types[file_extension]
        destination = f"tmp/tmp-{str(uuid4().hex)}.{file_extension}"
        
        try:
            if not self.minio_client.bucket_exists(bucket_name):
                self.minio_client.make_bucket(bucket_name)
            
            self.__make_public(bucket_name)

            # Upload file
            self.minio_client.fput_object(
                bucket_name=bucket_name,
                object_name=destination,
                file_path=source_file,
                content_type=content_type
            )

            preview_url = self.generate_presigned_url(
                object_name=destination,
                response_content_disposition="inline"
            ).split('?')[0]

            return preview_url

        except S3Error as s3_error:
            raise s3_error

    
    def download_file_from_minio(self, url: str):
        """This downloads a file from a minio url to a temporary folder

        Args:
            url (str): File url
        """

        try:
            # Get save file extension from url
            save_file_extension = url.split('.')[-1]

            # Configure save path to save file to temporary directory
            save_path = os.path.join(settings.TEMP_DIR, f'tmp-{str(uuid4().hex)}.{save_file_extension}')
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            return save_path
        
        except requests.RequestException as e:
            print(f"Error downloading large file: {e}")


minio_service = MinioService()