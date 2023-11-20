import os
import logging

from app.conf import (
    s3_cfg,
    geolocation_cfg,
    spocs_cfg,
    adzerk_cfg,
    domain_affinities_cfg,
)

env = os.environ.get('APP_ENV') or 'development'
release = os.environ.get('GIT_SHA') or 'local'
logging.info("APP_ENV = " + env)

s3 = getattr(s3_cfg, env)
geolocation = getattr(geolocation_cfg, env)
spocs = getattr(spocs_cfg, env)
adzerk = getattr(adzerk_cfg, env)
domain_affinities = getattr(domain_affinities_cfg, env)
