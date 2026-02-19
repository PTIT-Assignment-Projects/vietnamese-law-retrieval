from collections import defaultdict, Counter
from typing import Dict, List


class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(list)
        self.doc_lengths = {}
        self.doc_terms = defaultdict(Counter)
        self.total_docs = 0
        self.avg_doc_length = 0
    def build(self, documents: Dict[str, List[str]]) -> None:
        pass