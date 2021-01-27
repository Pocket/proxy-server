import tempfile

import geoip2.database

from app.conf import geolocation


class Factory():

    def __init__(self, s3):
        self.s3 = s3

    def get_instance(self):
        """
        :return: geoip2.database.Reader
        """
        with tempfile.TemporaryFile() as fp:
            self.s3.download_fileobj(geolocation['s3_bucket'], geolocation['s3_key'], fp)
            fp.seek(0)
            return geoip2.database.Reader(fp, mode=geoip2.database.MODE_FD)
