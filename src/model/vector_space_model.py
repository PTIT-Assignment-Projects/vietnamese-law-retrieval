import math
from typing import List, Tuple, Counter

from src.indexing.inverted_index import InvertedIndex
from src.model.model import Model


class VectorSpaceModel(Model):
    def __init__(self, inverted_index: InvertedIndex):
        super().__init__()
        self.index = inverted_index
        self.idf_cache = {}
    def compute_idf(self, term: str) -> float:
        """compute IDf for a term"""
        if term not in self.idf_cache:
            df = self.index.get_doc_frequency(term)
            if df > 0:
                # idf smoothing like in sklearn
                self.idf_cache[term] = math.log((self.index.total_docs + 1) / (1 + df)) + 1
            else:
                self.idf_cache[term] = 0
        return self.idf_cache[term]
    def compute_tf_idf(self, term: str, doc_id: str) -> float:
        """Compute TF-IDF score for a term in a document"""
        tf = self.index.get_term_frequency(term, doc_id)
        if tf == 0:
            return 0
        tf_normalized = 1 + math.log(tf)
        idf = self.compute_idf(term)
        return tf_normalized * idf
    def search(self, query_terms: List[str], top_n: int = 10) -> List[Tuple[str, float]]:
        """Search using cosine similarity with TF-IDF"""
        if not query_terms:
            return []
        # Get candidate documents (union of all documents containing any query term)
        candidates = set()
        for term in query_terms:
            candidates.update(self.index.get_docs_contain_term(term))
        if not candidates:
            return []
        query_tf = Counter(query_terms)
        query_vector = {} # term -> idf value
        query_norm = 0

        for term, freq in query_tf.items():
            tf_normalized = 1 + math.log(freq)
            idf = self.compute_idf(term)
            tf_idf_value = tf_normalized * idf
            query_vector[term] = tf_idf_value
            query_norm += tf_idf_value ** 2
        query_norm = math.sqrt(query_norm)
        # compute cosine similarity for each candidate document
        scores = []
        for doc_id in candidates:
            dot_product = 0
            doc_norm = 0

            # only consider terms appeared in both query and document
            for term in query_terms:
                if term in self.index.term_docs:
                    doc_tfidf = self.compute_tf_idf(term, doc_id)
                    dot_product += query_vector[term] * doc_tfidf
            # compute document norm
            for term, freq in self.index.doc_terms[doc_id].items():
                doc_tfidf = self.compute_tf_idf(term, doc_id)
                doc_norm += doc_tfidf ** 2
            doc_norm = math.sqrt(doc_norm)

            # cosine similarity
            if doc_norm > 0 and query_norm > 0:
                similarity = dot_product / (query_norm * doc_norm)
                scores.append((doc_id, similarity))
        # Sort by score and return the top n results
        scores.sort(key = lambda x : x[1], reverse=True)
        return scores[:top_n]