from typing import List

from src.indexing.inverted_index import InvertedIndex
from src.util.constant import AND_OPERATOR, OR_OPERATOR, NOT_OPERATOR


class BooleanRetrieval:
    """Boolean retrieval model"""

    def __init__(self, inverted_index: InvertedIndex):
        self.index = inverted_index
    def search(self, query_terms: List[str]) -> List[str]:
        """Search using boolean operators
        Args:
            query_terms (List[str]): list of query terms
        """
        query_term_set = {AND_OPERATOR, OR_OPERATOR, NOT_OPERATOR}
        if not query_terms:
            return []
        first_term = []
        second_term = []
        is_first_term = True
        operator = ""
        for term in query_terms:
            if term in query_term_set:
                is_first_term = False
                operator = term
                continue
            if is_first_term:
                first_term.append(term)
            else:
                second_term.append(term)
        # print("first query terms: ", first_term, "second terms: ", second_term)
        if operator == "":
            operator = AND_OPERATOR
        if operator == AND_OPERATOR:
            # intersection all document sets
            all_and_terms = first_term + second_term
            if not all_and_terms:
                return []

            result = self.index.get_docs_contain_term(all_and_terms[0])
            for term in all_and_terms[1:]:
                result = result.intersection(self.index.get_docs_contain_term(term))
            return list(result)
        elif operator == OR_OPERATOR:
            # Union
            result = set()
            for term in first_term:
                result = result.union(self.index.get_docs_contain_term(term))
            for term in second_term:
                result = result.union(self.index.get_docs_contain_term(term))
            return list(result)
        elif operator == NOT_OPERATOR:
            # All documents minus the ones containing the terms
            all_docs = set(self.index.doc_lengths.keys())
            excluded = set()
            for term in first_term:
                excluded = excluded.union(self.index.get_docs_contain_term(term))
            for term in second_term:
                excluded = excluded.union(self.index.get_docs_contain_term(term))
            return list(all_docs - excluded)
        return []