import json
import logging

import boto3


logger = logging.getLogger("backend")


class SecretsManager:
    """Encapsulates Secrets Manager functions."""

    def __init__(self) -> None:
        self.secretsmanager_client = boto3.client("secretsmanager")
        # print("region", self.secretsmanager_client.meta.region_name)

    def get_secret(self, name, key):
        kwargs = {"SecretId": name}
        response = self.secretsmanager_client.get_secret_value(**kwargs)
        return json.loads(response["SecretString"])[key]

    def try_get_secret(self, name, key):
        try:
            logger.info("Getting secret from Secrets Manager", name, key)
            return self.get_secret(name, key)
        except Exception:
            logger.error("Failed to get secret", exc_info=True)
            return None
