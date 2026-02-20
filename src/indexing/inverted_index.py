from collections import defaultdict, Counter
from typing import Dict, List, Set


class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(list)
        self.doc_lengths = {}
        self.doc_terms = defaultdict(Counter)
        self.total_docs = 0
        self.avg_doc_length = 0
    def build(self, documents: Dict[str, List[str]]) -> None:
        self.total_docs = len(documents)
        total_length = 0
        for cid, terms in documents.items():
            doc_length = len(terms)
            self.doc_lengths[cid] = doc_length
            total_length += doc_length

            term_counts = Counter(terms)
            self.doc_terms[cid] = term_counts

            # build inverted index with positions
            for pos, term in enumerate(terms):
                self.index[term].append((cid, pos))
        self.avg_doc_length = total_length / self.total_docs if self.total_docs > 0 else 0
    def get_docs_contain_term(self, term: str) -> Set[str]:
        """Get document ids containing the given term"""
        return set(doc_id for doc_id, _ in self.index.get(term, []))
    def get_term_frequency(self, term: str, doc_id: str) -> int:
        """Get frequency of term (TF) in a document"""
        return self.doc_terms[doc_id].get(term, 0)
    def get_doc_frequency(self, term: str) -> int:
        """Get the number of documents containing the given term (DF)"""
        return len(self.get_docs_contain_term(term))
