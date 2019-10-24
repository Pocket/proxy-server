import geoip2.database
import os


def get_mocked_geolocation_factory():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, 'GeoIP2-City-Test.mmdb')
    return geoip2.database.Reader(file_path)
