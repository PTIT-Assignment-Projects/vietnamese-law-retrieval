from abc import abstractmethod, ABC
from typing import List, Tuple


class Model(ABC):
    def __init__(self):
        self.index = None
    @abstractmethod
    def search(self, query_terms: List[str], top_n: int = 10) -> List[Tuple[str, float]]:
        """Search using the model
        Args:
            query_terms (List[str]): list of query terms
            top_n (int, optional): top n results. Defaults to 10.
        Returns:
            List of (doc_id, score) tuples
        """
        pass