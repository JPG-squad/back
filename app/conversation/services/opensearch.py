import json
import logging
import os

import boto3
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection

from app.settings import APP_ENV, LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


class OpensearchService:
    def __init__(self):
        if APP_ENV == "dev":
            logger.info("Using dev OpenSearch")
            self.open_search = OpenSearch(hosts=os.getenv('OPENSEARCH_HOST'))
            logger.info("Connected dev OpenSearch!")
        elif APP_ENV == "prod":
            logger.info("Using prod OpenSearch")
            credentials = boto3.Session().get_credentials()
            auth = AWSV4SignerAuth(credentials, 'eu-south-2')
            self.open_search = OpenSearch(
                hosts=os.getenv('OPENSEARCH_HOST'),
                http_auth=auth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
            )
            logger.info("Connected prod OpenSearch!")
        else:
            self.open_search = None
            logger.info("DRP does not haves opensearch at the moment!")

    def index_conversation(self, conversation):
        c_to_index = {
            "object_type": "conversation",
            "id": conversation.id,
            "title": conversation.title,
            "description": conversation.description,
            "patient_id": conversation.patient.id,
            "status": conversation.status,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "duration": conversation.duration,
        }
        if conversation.conversation:
            conversation_arr = json.loads(conversation.conversation)["conversation"]
            c_to_index["conversation"] = conversation_arr
        try:
            self.open_search.index(
                index="jpg.object", id=f"{c_to_index['object_type']}-{c_to_index['id']}", body=c_to_index
            )
            logger.info(f"Indexed conversation {c_to_index['id']}")
        except Exception:
            logger.error(c_to_index)
            logger.exception(f"Error indexing conversation {c_to_index['id']}")

    def search_conversation(self, text):
        """Search a text inside all conversation and returns that text with <em> tag."""
        try:
            response = self.open_search.search(
                index="jpg.object",
                body={
                    "query": {"multi_match": {"query": text, "type": "most_fields", "fields": ["*"]}},
                    'highlight': {'fields': {'*': {}}, 'pre_tags': '<b>', 'post_tags': '</b>'},
                },
            )
            hits = response["hits"]["total"]["value"]
            logger.info(f"Search conversation with text{text} total hits {hits}")
            # Extract the highlighted conversation object from the response hits
            if response["hits"]["total"]["value"] == 0:
                return []
            results = []
            for hit in response["hits"]["hits"]:
                hightlight = hit["highlight"]
                hightlight["conversation_id"] = hit["_source"]["id"]
                results.append(hit["highlight"])
            return results
        except Exception:
            logger.exception(f"Error searching conversation with text {text}")


# TO BE IMPROVED, improving the arcitecture and all
open_search_service = OpensearchService()
