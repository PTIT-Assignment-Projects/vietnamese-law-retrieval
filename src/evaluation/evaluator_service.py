import ast
from typing import List, Dict

import pandas as pd

from src.evaluation.evaluation_metrics import calculate_precision_at_k, calculate_recall_at_k, calculate_f1_at_k, \
    reciprocal_rank, calculate_average_precision, mean_reciprocal_rank
from src.preprocessing.text_processor import TextProcessor
from src.search_engine import SearchEngine
from src.util import constant
from src.util.constant import VSM_MODEL_NAME, BM25_MODEL_NAME, BOOLEAN_RETRIEVAL_NAME
from src.util.pickle_handling import save_to_pickle_file, load_pickle_file


class EvaluatorService:
    DEFAULT_K_VALUES = [1, 2, 3, 5, 10]
    MODEL_LIST = [VSM_MODEL_NAME, BM25_MODEL_NAME, BOOLEAN_RETRIEVAL_NAME]
    def __init__(self, search_engine: SearchEngine):
        self.processor = TextProcessor()
        self.search_engine = search_engine
        self.ground_truth = {} # qid -> list of cid
        self.raw_documents = {} # qid -> document
        self.k_values = EvaluatorService.DEFAULT_K_VALUES
    @staticmethod
    def _parse_cid(cid_value) -> List[str]:
        """
        Parse the ``cid`` column which may be stored as a string
        representation of a Python list, e.g. ``"[3159]"`` or ``"[1, 2, 3]"``.
        Always returns a list of **string** IDs so they match the search
        engine output format.
        """
        if isinstance(cid_value, list):
            return [str(c) for c in cid_value]
        try:
            parsed = ast.literal_eval(str(cid_value))
            if isinstance(parsed, list):
                return [str(c) for c in parsed]
            return [str(parsed)]
        except (ValueError, SyntaxError):
            return [str(cid_value)]
    def build_ground_truth(self):
        df = pd.read_csv(constant.TRAIN_TEST_MERGED_PATH)
        for _, row in df.iterrows():
            qid = row[constant.QID_COLUMN]
            cid_list = self._parse_cid(row[constant.CID_COLUMN])
            self.ground_truth[qid] = cid_list
            text_value = row[constant.QUESTION_COLUMN]
            raw_document = str(text_value) if pd.notna(text_value) else None
            self.raw_documents[qid] = raw_document
        save_to_pickle_file(constant.GROUND_TRUTH_EVALUATION_DOCUMENT_PATH, self.ground_truth)
        save_to_pickle_file(constant.RAW_EVALUATION_DOCUMENT_PATH, self.raw_documents)
    def load_ground_truth(self):
        try:
            self.ground_truth = load_pickle_file(constant.GROUND_TRUTH_EVALUATION_DOCUMENT_PATH)
            self.raw_documents = load_pickle_file(constant.RAW_EVALUATION_DOCUMENT_PATH)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "Processed documents not found. Run build_ground_truth() first."
            ) from e
    def evaluate(self, method: str = BM25_MODEL_NAME, top_n: int = 10) -> Dict:
        all_retrieved: List[List[str]] = []
        all_relevant: List[List[str]] = []
        per_query_results: List[Dict] = []
        total = len(self.raw_documents)
        for qid, question in self.raw_documents.items():
            true_ids = self.ground_truth[qid]
            all_relevant.append(true_ids)
            try:
                results = self.search_engine.search(question, method=method, top_n=top_n)
                retrieved_ids = [str(doc_id) for doc_id, _ in results]
            except Exception as e:
                retrieved_ids = []
            all_retrieved.append(retrieved_ids)

            query_metrics: Dict = {"qid": qid, "query": question}
            for k in self.k_values:
                query_metrics[f"precision@{k}"] = calculate_precision_at_k(
                    retrieved_ids, true_ids, k
                )
                query_metrics[f"recall@{k}"] = calculate_recall_at_k(
                    retrieved_ids, true_ids, k
                )
                query_metrics[f"f1@{k}"] = calculate_f1_at_k(
                    retrieved_ids, true_ids, k
                )
            query_metrics["rr"] = reciprocal_rank(retrieved_ids, true_ids)
            query_metrics["ap"] = calculate_average_precision(retrieved_ids, true_ids)
            per_query_results.append(query_metrics)
        aggregated: Dict = {}
        for k in self.k_values:
            aggregated[f"precision@{k}"] = self._mean(
                [q[f"precision@{k}"] for q in per_query_results]
            )
            aggregated[f"recall@{k}"] = self._mean(
                [q[f"recall@{k}"] for q in per_query_results]
            )
            aggregated[f"f1@{k}"] = self._mean(
                [q[f"f1@{k}"] for q in per_query_results]
            )
        aggregated["mrr"] = mean_reciprocal_rank(all_retrieved, all_relevant)
        aggregated["map"] = self._mean(
            [q["ap"] for q in per_query_results]
        )
        aggregated["total_queries"] = total
        return aggregated
    def run_evaluation_and_save(self) -> None:
        results = []
        for method in EvaluatorService.MODEL_LIST:
            result = self.evaluate(method=method)
            result["method"] = method
            results.append(result)
        df = pd.DataFrame(results)
        df.to_csv(constant.EVALUATION_RESULT_FILE_PATH, index = False)


    @staticmethod
    def _mean(values: List[float]) -> float:
        return sum(values) / len(values) if values else 0.0