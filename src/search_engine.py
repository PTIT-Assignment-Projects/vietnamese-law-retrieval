from collections import defaultdict

from src.indexing.inverted_index import InvertedIndex
from src.preprocessing.preprocessing import load_data
from src.preprocessing.text_processor import TextProcessor
from src.util.constant import CORPUS_PATH, CID_COLUMN, TEXT_COLUMN, RAW_CORPUS_DICT_PATH, PROCESSED_CORPUS_DICT_PATH
from src.util.pickle_handling import save_to_pickle_file, load_pickle_file


class SearchEngine:
    def __init__(self):
        self.processor = TextProcessor()
        self.inverted_index = InvertedIndex()
        self.boolean_retrieval = None
        self.vsm = None
        self.bm25 = None
        self.raw_documents = defaultdict(str)
        self.processed_documents = defaultdict(list)
    def process_documents(self):
        corpus = load_data(CORPUS_PATH)
        for _, row in corpus.iterrows():
            cid = row[CID_COLUMN]
            raw_document = str(row[TEXT_COLUMN]) if row[TEXT_COLUMN] is not None else ""
            self.raw_documents[cid] = raw_document
            save_to_pickle_file(RAW_CORPUS_DICT_PATH, self.raw_documents)
            processed = self.processor.process_text(raw_document)
            self.processed_documents[cid] = processed
            save_to_pickle_file(PROCESSED_CORPUS_DICT_PATH, self.processed_documents)
    def _load_processed_documents(self):
        self.raw_documents = load_pickle_file(RAW_CORPUS_DICT_PATH)
        self.processed_documents = load_pickle_file(PROCESSED_CORPUS_DICT_PATH)
    def build_index(self):
        self._load_processed_documents()
        self.inverted_index.build(self.processed_documents)



def main():
    search_engine = SearchEngine()
    search_engine.build_index()
main()
