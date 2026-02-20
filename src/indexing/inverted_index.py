from collections import defaultdict, Counter
from typing import Dict, List, Set


class InvertedIndex:
    def __init__(self):
        """
        Initialize the InvertedIndex's internal data structures and counters.
        
        Sets up:
        - index: mapping from term to list of (doc_id, position) occurrences.
        - doc_lengths: mapping from doc_id to document length (number of terms).
        - doc_terms: mapping from doc_id to a Counter of term frequencies for that document.
        - total_docs: total number of documents indexed (starts at 0).
        - avg_doc_length: average document length across indexed documents (starts at 0).
        """
        self.index = defaultdict(list)
        self.doc_lengths = {}
        self.doc_terms = defaultdict(Counter)
        self.total_docs = 0
        self.avg_doc_length = 0
    def build(self, documents: Dict[str, List[str]]) -> None:
        """
        Builds the inverted index and per-document statistics from the provided documents.
        
        Updates internal state with:
        - index: maps each term to a list of (doc_id, position) occurrences,
        - doc_lengths: length (number of terms) for each document,
        - doc_terms: per-document term frequency counters,
        - total_docs: number of documents processed,
        - avg_doc_length: average document length across all indexed documents.
        
        Parameters:
            documents (Dict[str, List[str]]): Mapping from document ID to the list of term tokens for that document.
        """
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
        """
        Retrieve the set of document IDs that contain the specified term.
        
        Returns:
            Set[str]: Document IDs that include the term; empty set if the term is not present.
        """
        return set(doc_id for doc_id, _ in self.index.get(term, []))
    def get_term_frequency(self, term: str, doc_id: str) -> int:
        """
        Retrieve the frequency of a term within a specific document.
        
        Returns:
            int: The number of occurrences of `term` in `doc_id`.
        
        Raises:
            KeyError: If `doc_id` is not present in the index's document term mapping.
        """
        return self.doc_terms[doc_id].get(term, 0)
    def get_doc_frequency(self, term: str) -> int:
        """
        Compute the number of documents that contain the specified term.
        
        Returns:
            int: The number of documents that contain `term`.
        """
        return len(set(doc_id for doc_id, _ in self.index.get(term, [])))