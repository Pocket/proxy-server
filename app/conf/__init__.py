from os import environ
import logging

env = environ.get('APP_ENV') or 'development'
logging.info("APP_ENV = " + env)

from app.conf import s3, geolocation, spocs, adzerk, domain_affinities

s3 = getattr(s3, env)
geolocation = getattr(geolocation, env)
spocs = getattr(spocs, env)
adzerk = getattr(adzerk, env)
domain_affinities = getattr(domain_affinities, env)
