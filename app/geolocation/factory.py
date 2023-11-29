import os
import tempfile

import boto3
import geoip2.database
from google.cloud import storage

from app import conf
from app.conf import geolocation


class Factory:
    def __init__(self):
        if os.environ.get("GEOIP_GCS_BUCKET", None):
            self.storage_provider = "GCS"
            self.storage_client = storage.Client()

        else:
            self.storage_provider = "S3"
            self.storage_client = boto3.session.Session(**conf.s3["session"]).client(
                "s3", **conf.s3["client"]
            )

    def get_instance(self):
        """
        :return: geoip2.database.Reader
        """
        with tempfile.TemporaryFile() as fp:
            if self.storage_provider == "GCS":
                bucket = self.storage_client.bucket(os.environ.get("GEOIP_GCS_BUCKET"))
                blob = bucket.blob("GeoIP2-City.mmdb")

                blob.download_to_file(fp)

            else:
                self.storage_client.download_fileobj(
                    geolocation["s3_bucket"], geolocation["s3_key"], fp
                )

            fp.seek(0)

            return geoip2.database.Reader(fp, mode=geoip2.database.MODE_FD)
