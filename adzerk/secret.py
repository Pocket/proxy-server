import os
import boto3
import json
from botocore.exceptions import BotoCoreError
from functools import lru_cache


class ApplicationSecretException(Exception):
    pass


@lru_cache()
def get_api_key():
    '''
    Get and cache an API key for Kevel
    @return: str: api
    '''
    try:
        secret_name = os.environ.get("ADZERK_SECRET_NAME")

        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name='us-east-1'
        )

        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        secret = json.loads(get_secret_value_response['SecretString'])
        return secret['ADZERK_API_KEY']
    except BotoCoreError as e:
        # Try to get Sentry DSN from environment variable if SecretsManager fails.
        # This is intended only for development.
        secret = os.environ.get('ADZERK_API_KEY')
        if secret:
            return secret
        else:
            raise ApplicationSecretException("Failed to get AdZerk API key")


def clear_api_key_cache():
    get_api_key.cache_clear()
