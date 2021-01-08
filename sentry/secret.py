import os
import json

import boto3
from botocore.exceptions import BotoCoreError


class ApplicationSecretException(Exception):
    pass


def get_sentry_dsn():
    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name='us-east-1'
        )

        secret_name = os.environ.get("SENTRY_DSN_SECRET_NAME")
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        secret = json.loads(get_secret_value_response['SecretString'])
        return secret['SENTRY_DSN']
    except BotoCoreError as e:
        # Try to get Sentry DSN from environment variable if SecretsManager fails.
        secret_dsn = os.environ.get("SENTRY_DSN")
        if secret_dsn:
            return secret_dsn
        else:
            raise ApplicationSecretException("Failed to get Sentry DSN")
