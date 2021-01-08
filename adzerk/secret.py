import os
import boto3
import json
from botocore.exceptions import BotoCoreError


class ApplicationSecretException(Exception):
    pass


def get_api_key():
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
        secret = os.environ.get('ADZERK_API_KEY')
        if secret:
            return secret
        else:
            raise ApplicationSecretException("Failed to get AdZerk API key")
