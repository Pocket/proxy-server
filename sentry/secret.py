import os
import boto3
import json


def get_sentry_dsn():
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name='us-east-1'
    )

    secret_name = os.environ.get("SENTRY_DSN_SECRET_NAME")
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    secret = json.loads(get_secret_value_response['SecretString'])
    return secret['SENTRY_DSN']
