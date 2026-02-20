from collections import defaultdict

from src.indexing.inverted_index import InvertedIndex
from src.preprocessing.preprocessing import load_data
from src.preprocessing.text_processor import TextProcessor
from src.util.constant import CORPUS_PATH, CID_COLUMN, TEXT_COLUMN, RAW_CORPUS_DICT_PATH, PROCESSED_CORPUS_DICT_PATH
from src.util.pickle_handling import save_to_pickle_file, load_pickle_file


class SearchEngine:
    def __init__(self):
        """
        Initialize SearchEngine state: create text processor and inverted index, and allocate storage for retrieval models and corpus data.
        
        Attributes:
            processor: TextProcessor instance used to normalize and tokenize documents.
            inverted_index: InvertedIndex instance used to build and query the index.
            boolean_retrieval: Placeholder for a boolean retrieval model (initially None).
            vsm: Placeholder for a vector-space model instance (initially None).
            bm25: Placeholder for a BM25 model instance (initially None).
            raw_documents: defaultdict(str) mapping document IDs to raw text.
            processed_documents: defaultdict(list) mapping document IDs to token lists or processed representations.
        """
        self.processor = TextProcessor()
        self.inverted_index = InvertedIndex()
        self.boolean_retrieval = None
        self.vsm = None
        self.bm25 = None
        self.raw_documents = defaultdict(str)
        self.processed_documents = defaultdict(list)
    def process_documents(self):
        """
        Populate the engine's raw and processed document stores from the corpus and persist both to disk.
        
        Loads the corpus from CORPUS_PATH, iterates each row, saves the original text into self.raw_documents and a tokenized/normalized representation into self.processed_documents, and writes both mappings to RAW_CORPUS_DICT_PATH and PROCESSED_CORPUS_DICT_PATH respectively.
        """
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
        """
        Load previously saved corpus dictionaries into the search engine instance.
        
        This replaces the in-memory raw and processed document stores by loading serialized
        dictionaries from the configured pickle file paths and assigning them to
        `self.raw_documents` and `self.processed_documents`.
        """
        self.raw_documents = load_pickle_file(RAW_CORPUS_DICT_PATH)
        self.processed_documents = load_pickle_file(PROCESSED_CORPUS_DICT_PATH)
    def build_index(self):
        """
        Builds the inverted index from persisted processed documents.
        
        Ensures processed document dictionaries are loaded from persistent storage, then constructs the inverted index using the in-memory `processed_documents`.
        """
        self._load_processed_documents()
        self.inverted_index.build(self.processed_documents)



def main():
    search_engine = SearchEngine()
    search_engine.build_index()
main()