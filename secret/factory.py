import os
import json
from functools import lru_cache

import boto3
from botocore.exceptions import BotoCoreError


class SecretProviderException(Exception):
    pass


class SecretProvider:

    def __init__(self, name, key):
        self.name = name
        self.key = key

    @lru_cache()
    def get_value(self) -> str:
        """
        Get the secret value
        @return: str: api
        """
        try:
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name='us-east-1'
            )

            response = client.get_secret_value(SecretId=self.name)
            secret = json.loads(response['SecretString'])
            return secret[self.key]
        except BotoCoreError:
            # Fall back to an environment variable. This is intended only for development.
            secret = os.environ.get(self.key)
            if secret is not None:
                return secret

            raise SecretProviderException(f"Failed to get {self.name}")

    def clear_cache(self):
        self.get_value.cache_clear()
