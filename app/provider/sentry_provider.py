import logging

import sentry_sdk

from app import conf
from starlette.requests import ClientDisconnect


SENTRY_IGNORE_ERRORS = (
    ClientDisconnect
)


def before_send(event, hint):
    if hint and "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]
        if isinstance(exc_value, SENTRY_IGNORE_ERRORS):
            return None

    return event


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
            before_send=before_send
    )

