import os
from typing import Optional

from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers

from src.preprocessing.text_processor import TextProcessor
from src.util.constant import PROCESSED_INDEX_NAME, NORMAL_INDEX_NAME, RAW_CORPUS_DICT_PATH, PROCESSED_CORPUS_DICT_PATH
from src.util.pickle_handling import load_pickle_file

load_dotenv()
class ElasticSearchIndexing:
    def __init__(self):
        self.es: Optional[Elasticsearch] = None
        self.processor = TextProcessor()
        self.mapping = {
            "mappings": {
                "properties": {
                    "content": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword", "ignore_above": 256}
                        }
                    }
                }
            }
        }
        self.raw_documents = {}
        self.processed_documents = {}
        self._load_processed_documents()
        self._connect_to_client()
    def _connect_to_client(self):
        elastic_host = os.getenv("ELASTIC_HOST", "localhost:9092")
        self.es = Elasticsearch(elastic_host)
        self._create_index_if_not_exists(PROCESSED_INDEX_NAME)
        self._create_index_if_not_exists(NORMAL_INDEX_NAME)
    def _create_index_if_not_exists(self, index_name: str) -> None:
        if self.es.indices.exists(index = index_name):
            self.es.indices.delete(index = index_name)
        self.es.indices.create(index = index_name, body = self.mapping)
    def _load_processed_documents(self):
        try:
            self.raw_documents = load_pickle_file(RAW_CORPUS_DICT_PATH)
            self.processed_documents = load_pickle_file(PROCESSED_CORPUS_DICT_PATH)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "Processed documents not found. Run process_documents() first."
            ) from e
    def ingest_normal_index(self):
        for doc_id, text in self.raw_documents.items():
            yield {
                "_index": NORMAL_INDEX_NAME,
                "_id": doc_id,
                "_source": {
                    "content": text
                }
            }
    def ingest_processed_index(self):
        for doc_id, token_list in self.processed_documents.items():
            yield {
                "_index": PROCESSED_INDEX_NAME,
                "_id": doc_id,
                "_source": {
                    "content": " ".join(token_list)
                }
            }
    def ingest_to_elasticsearch(self):
        success, failed = helpers.bulk(self.es, self.ingest_normal_index())
        print(f"{success} documents index in normal index, {failed} failed")
        success, failed = helpers.bulk(self.es, self.ingest_processed_index())
        print(f"{success} documents index in processed index, {failed} failed")
