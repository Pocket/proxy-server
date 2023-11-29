import logging

import boto3
from google.cloud import storage

from app import conf
from app.geolocation.factory import Factory as GeolocationFactory


class GeolocationProvider:
    __PROVIDER_INSTANCE = None

    def __init__(self):
        if not GeolocationProvider.__PROVIDER_INSTANCE:
            s3 = boto3.session.Session(**conf.s3["session"]).client(
                "s3", **conf.s3["client"]
            )
            geolocation = GeolocationFactory(s3).get_instance()
            GeolocationProvider.__PROVIDER_INSTANCE = geolocation

    def __setattr__(self, key, value):
        if GeolocationProvider.__PROVIDER_INSTANCE:
            raise AttributeError("Already instantiated")

    @classmethod
    def get_city(cls, ip):
        return cls.__PROVIDER_INSTANCE.city(ip)

    @classmethod
    def get_country(cls, city):
        if city:
            return city.country.iso_code
        else:
            logging.warning("No city returned")

    @classmethod
    def get_region(cls, city):
        if city:
            return city.subdivisions.most_specific.iso_code
        else:
            logging.warning("No city returned")
