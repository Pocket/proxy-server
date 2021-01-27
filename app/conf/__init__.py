import os
import logging

env = os.environ.get('APP_ENV') or 'development'
release = os.environ.get('GIT_SHA') or 'local'
logging.info("APP_ENV = " + env)

from app.conf import s3, geolocation, spocs, adzerk, domain_affinities

s3 = getattr(s3, env)
geolocation = getattr(geolocation, env)
spocs = getattr(spocs, env)
adzerk = getattr(adzerk, env)
domain_affinities = getattr(domain_affinities, env)
