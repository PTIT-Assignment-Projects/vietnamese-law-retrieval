from collections import defaultdict
from textwrap import dedent
from typing import List, Tuple, Optional

import pandas as pd

from src.indexing.inverted_index import InvertedIndex
from src.model.bm25 import OkapiBM25
from src.model.boolean_retrieval import BooleanRetrieval
from src.model.vector_space_model import VectorSpaceModel
from src.preprocessing.preprocessing import load_data
from src.preprocessing.text_processor import TextProcessor
from src.util import constant
from src.util.constant import CORPUS_PATH, CID_COLUMN, TEXT_COLUMN, RAW_CORPUS_DICT_PATH, PROCESSED_CORPUS_DICT_PATH, \
    VSM_MODEL_INDEX_BUILT_PATH, BM25_MODEL_INDEX_BUILT_PATH, INVERTED_INDEX_BUILT_PATH
from src.util.pickle_handling import save_to_pickle_file, load_pickle_file


class SearchEngine:
    def __init__(self):
        self.processor = TextProcessor()
        self.inverted_index = InvertedIndex()
        self.boolean_retrieval: Optional[BooleanRetrieval] = None
        self.vsm: Optional[VectorSpaceModel] = None
        self.bm25: Optional[OkapiBM25] = None
        self.raw_documents = defaultdict(str)
        self.processed_documents = defaultdict(list)
    def process_documents(self):
        corpus = load_data(CORPUS_PATH)
        for _, row in corpus.iterrows():
            cid = row[CID_COLUMN]
            text_value = row[TEXT_COLUMN]
            raw_document = str(text_value) if pd.notna(text_value) else None
            self.raw_documents[cid] = raw_document
            processed = self.processor.process_text(raw_document)
            self.processed_documents[cid] = processed
        save_to_pickle_file(RAW_CORPUS_DICT_PATH, self.raw_documents)
        save_to_pickle_file(PROCESSED_CORPUS_DICT_PATH, self.processed_documents)

    def _load_processed_documents(self):
        try:
            self.raw_documents = load_pickle_file(RAW_CORPUS_DICT_PATH)
            self.processed_documents = load_pickle_file(PROCESSED_CORPUS_DICT_PATH)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "Processed documents not found. Run process_documents() first."
            ) from e
    def _build_index(self):
        self._load_processed_documents()
        self.inverted_index.build(self.processed_documents)
        save_to_pickle_file(INVERTED_INDEX_BUILT_PATH, self.inverted_index)
        self.vsm = VectorSpaceModel(self.inverted_index)
        save_to_pickle_file(VSM_MODEL_INDEX_BUILT_PATH, self.vsm)
        self.bm25 = OkapiBM25(self.inverted_index)
        save_to_pickle_file(BM25_MODEL_INDEX_BUILT_PATH, self.bm25)
    def load_prebuilt_index(self):
        try:

            self._load_processed_documents()
            self.inverted_index = load_pickle_file(INVERTED_INDEX_BUILT_PATH)
            self.boolean_retrieval = BooleanRetrieval(self.inverted_index)
            self.vsm = load_pickle_file(VSM_MODEL_INDEX_BUILT_PATH)
            self.bm25 = load_pickle_file(BM25_MODEL_INDEX_BUILT_PATH)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "Relevant model files not found. Run process_documents() and _build_index() first."
            ) from e
    def search(self, query: str, method: str = 'bm25', top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Search for documents matching the query
        :param query: Search query string.
        :param method: 'boolean', 'vsm', 'bm25'. Defaults to 'bm25'
        :param top_n: Top n results to return. Defaults to 10.
        :return: List of (doc_id, score) tuples.
        """
        query_terms = self.processor.process_text(query)
        if not query_terms:
            return []

        # search using correct method
        match method:
            case constant.BOOLEAN_RETRIEVAL_NAME:
                if self.boolean_retrieval is None:
                    raise RuntimeError("Boolean retrieval model not loaded. Call load_prebuilt_index() or _build_index() first.")
                doc_ids = self.boolean_retrieval.search(query_terms)
                return [(doc_id, 1.0) for doc_id in doc_ids[:top_n]]
            case constant.VSM_MODEL_NAME:
                if self.vsm is None:
                    raise RuntimeError("VSM model not loaded. Call load_prebuilt_index() or _build_index() first.")
                return self.vsm.search(query_terms, top_n)
            case constant.BM25_MODEL_NAME:
                if self.bm25 is None:
                    raise RuntimeError("BM25 model not loaded. Call load_prebuilt_index() or _build_index() first.")
                return self.bm25.search(query_terms, top_n)
            case _:
                raise ValueError(f"Unknown method: {method}")

    def display_results(self, results: List[Tuple[str, float]], query: str, method: str, max_length: int = 200):
        """Display search results"""
        print(dedent(f"""
                {'=' * 80}
                Query: '{query}'
                Method: '{method}'
                Found {len(results)} documents
                {'=' * 80}"""))
        for rank, (doc_id, score) in enumerate(results, 1):
            raw_text = self.raw_documents.get(doc_id) or ""
            processed_text = self.processed_documents.get(doc_id) or []
            preview = raw_text[:max_length].replace('\n', ' ')
            if len(raw_text) > max_length:
                preview += "..."
            print(dedent(f"""
                        \x1B[32m{rank}. {doc_id}\x1B[0m
                        Score: {score:.4f}
                        Preview: {preview}
                        Processed_text: {processed_text}
                        """))


