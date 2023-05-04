import logging
import os

import boto3
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection

from app.settings import APP_ENV, LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)

open_search = None

if APP_ENV == "dev":
    logger.info("Using dev OpenSearch")
    open_search = OpenSearch(hosts=os.getenv('OPENSEARCH_HOST'))
    logger.info("Connected dev OpenSearch!")
else:
    logger.info("Using prod OpenSearch")
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, 'eu-west-1')
    open_search = OpenSearch(
        hosts=os.getenv('OPENSEARCH_HOST'),
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )
    logger.info("Connected prod OpenSearch!")
