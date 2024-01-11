import logging

import sentry_sdk

from app import conf

def sentry_init():
    dsn = conf.sentry['dsn']
    traces_sample_rate = conf.sentry['traces_sample_rate']
    profiles_sample_rate = conf.sentry['profiles_sample_rate']
    if not dsn:
        return
    sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,
            environment=conf.env,
    )

