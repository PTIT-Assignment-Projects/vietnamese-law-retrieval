import math
from typing import List, Tuple

from src.indexing.inverted_index import InvertedIndex
from src.model.model import Model


class OkapiBM25(Model):
    """Okapi BM25 probabilistic retrieval model"""
    def __init__(self, inverted_index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        super().__init__()
        self.index = inverted_index
        self.k1 = k1 # Term frequency saturation parameter
        self.b = b # length normalization parameter
        self.idf_cache = {}
    def compute_idf(self, term) -> float:
        """Compute IDF of BM25 formula with smoothing(+1 inside log)"""
        if term not in self.idf_cache:
            df = self.index.get_doc_frequency(term)
            n = self.index.total_docs
            if df > 0:
                # BM25 idf formula with smoothing (+1)
                self.idf_cache[term] = math.log((n - df + 0.5) / (df + 0.5) + 1)
            else:
                self.idf_cache[term] = 0
        return self.idf_cache[term]
    def compute_bm25_score(self, term: str, doc_id: str) -> float:
        """Compute BM25 score for a term in document"""
        tf = self.index.get_term_frequency(term, doc_id)
        if tf == 0:
            return 0
        doc_length = self.index.doc_lengths[doc_id]
        avg_length = self.index.avg_doc_length

        #BM25 formula
        idf = self.compute_idf(term)
        numerator = tf * (self.k1 + 1)
        denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / avg_length))
        return idf * (numerator / denominator)
    def search(self, query_terms: List[str], top_n: int = 10) -> List[Tuple[str, float]]:
        """Search using BM25 scoring"""
        if not query_terms:
            return []
        # Get candidate documents
        candidates = set()
        for term in query_terms:
            candidates.update(self.index.get_docs_contain_term(term))
        if not candidates:
            return []
        # compute BM25 score for each candidate
        scores = []
        for doc_id in candidates:
            score = 0
            for term in query_terms:
                score += self.compute_bm25_score(term, doc_id)
            scores.append((doc_id, score))
        # sort by score and return top n results
        scores.sort(key = lambda x : x[1], reverse = True)
        return scores[:top_n]
