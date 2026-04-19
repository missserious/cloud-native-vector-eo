# minIO
import logging
import os

import boto3
from botocore.client import Config

logging.basicConfig(level=logging.INFO)


class MinioStorage:

    # establish client
    def __init__(self) -> None:
        endpoint = os.getenv("ENDPOINT")
        access_key = os.getenv("ACCESS_KEY")
        secret_key = os.getenv("SECRET_KEY")
        use_ssl = os.getenv("USE_SSL", "False").lower() == "true"
        region = os.getenv("REGION", "eu-central-1")

        self.bucket_name = os.getenv("BUCKET_NAME", "geo-bucket")

        self.s3 = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
            region_name=region,
            use_ssl=use_ssl,
        )

    def create_bucket(self) -> None:
        try:
            response = self.s3.list_buckets()
            existing_buckets = [b["Name"] for b in response["Buckets"]]

            if self.bucket_name not in existing_buckets:
                logging.info(f"Creating bucket: {self.bucket_name}")
                self.s3.create_bucket(Bucket=self.bucket_name)
            else:
                logging.info(f"Bucket already exists: {self.bucket_name}")

        except Exception as e:
            logging.info(f"Error while checking bucket '{self.bucket_name}': {e}")

    def upload_all_assets(self, assets: dict[str, str]) -> None:
        for key, file_path in assets.items():

            object_name = os.path.basename(file_path)

            self.s3.upload_file(
                Filename=file_path,
                Bucket=self.bucket_name,
                Key=object_name
            )

            logging.info(f"Uploaded: {object_name}")

    def upload_stac_file(self, file_path: str) -> None:
        object_name = os.path.basename(file_path)

        self.s3.upload_file(
            Filename=file_path,
            Bucket=self.bucket_name,
            Key=object_name
        )

        logging.info(f"Uploaded STAC: {object_name}")



    # ---------------------
    # SIGN Tiles URL
    # ---------------------
    def get_signed_url(self, object_name: str, expires: int = 3600) -> str:
        url = self.s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": object_name
            },
            ExpiresIn=expires
        )

        logging.info(f"SIGNED URL: {url}")

        return url