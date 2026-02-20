from typing import List, Tuple

from src.indexing.inverted_index import InvertedIndex


class BooleanRetrieval:
    """Boolean retrieval model"""

    def __init__(self, inverted_index: InvertedIndex):
        self.index = inverted_index
    def search(self, query_terms: List[str], operator: str = "AND") -> List[str]:
        pass
