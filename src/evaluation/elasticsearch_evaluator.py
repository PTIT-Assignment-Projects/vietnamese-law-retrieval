import logging
from typing import List, Dict

import pandas as pd
from dotenv import load_dotenv

from src.evaluation.evaluation_metrics import calculate_precision_at_k, calculate_recall_at_k, calculate_f1_at_k, \
    reciprocal_rank, calculate_average_precision, mean_reciprocal_rank
from src.evaluation.evaluator_service import EvaluatorService
from src.indexing.elasticsearch_indexing import ElasticSearchIndexing
from src.preprocessing.text_processor import TextProcessor
from src.util.constant import RAW_EVALUATION_DOCUMENT_PATH, GROUND_TRUTH_EVALUATION_DOCUMENT_PATH, \
    EVALUATION_ES_RESULT_FILE_PATH
from src.util.pickle_handling import load_pickle_file

class ElasticsearchEvaluator:
    DEFAULT_K_VALUES = (1, 2, 3, 5, 10)
    def __init__(self):
        self.processor = TextProcessor()
        self.ground_truth = {}  # qid -> list of cid
        self.raw_documents = {}  # qid -> document
        self.k_values = self.DEFAULT_K_VALUES
        self.es: ElasticSearchIndexing = ElasticSearchIndexing()
        self.load_ground_truth()

    def load_ground_truth(self):
        try:
            self.ground_truth = load_pickle_file(GROUND_TRUTH_EVALUATION_DOCUMENT_PATH)
            self.raw_documents = load_pickle_file(RAW_EVALUATION_DOCUMENT_PATH)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "Ground-truth evaluation files not found. Run build_ground_truth() first."
            ) from e
    def evaluate(self, top_n: int = 10, is_normal_index = True) -> Dict:
        all_retrieved: List[List[str]] = []
        all_relevant: List[List[str]] = []
        per_query_results: List[Dict] = []
        total = 0
        for qid, question in self.raw_documents.items():
            true_ids = self.ground_truth.get(qid, [])
            if not true_ids:
                logging.warning(f"No ground truth found for qid={qid}, skipping")
                continue
            total += 1
            all_relevant.append(true_ids)
            try:
                results = self.es.search(question, top_n=top_n, is_normal_index=is_normal_index)
                retrieved_ids = [str(hit["_id"]) for hit in results]
            except Exception:
                logging.warning(f"Search failed for qid={qid}")
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
            aggregated[f"precision@{k}"] = EvaluatorService.mean(
                [q[f"precision@{k}"] for q in per_query_results]
            )
            aggregated[f"recall@{k}"] = EvaluatorService.mean(
                [q[f"recall@{k}"] for q in per_query_results]
            )
            aggregated[f"f1@{k}"] = EvaluatorService.mean(
                [q[f"f1@{k}"] for q in per_query_results]
            )
        aggregated["mrr"] = mean_reciprocal_rank(all_retrieved, all_relevant)
        aggregated["map"] = EvaluatorService.mean(
            [q["ap"] for q in per_query_results]
        )
        aggregated["total_queries"] = total
        return aggregated
    def run_evaluation_and_save(self) -> None:
        results = []
        for is_normal_index in (True, False):
            result = self.evaluate(is_normal_index=is_normal_index)
            result["method"] = "normal_index" if is_normal_index else "processed_index"
            results.append(result)
        df = pd.DataFrame(results)
        df.to_csv(EVALUATION_ES_RESULT_FILE_PATH, index = False)