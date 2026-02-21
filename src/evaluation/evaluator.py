import ast
import time
from typing import List, Dict, Optional

import pandas as pd

from src.evaluation.evaluation_metrics import (
    calculate_precision_at_k,
    calculate_recall_at_k,
    calculate_f1_at_k,
    reciprocal_rank,
    mean_reciprocal_rank,
    calculate_average_precision,
)
from src.search_engine import SearchEngine
from src.util.constant import TRAIN_PATH, TEST_PATH


class Evaluator:
    """
    Evaluates the search engine against ground-truth query–relevance data.

    Workflow
    --------
    1. Load ``train.csv`` and ``test.csv``.
    2. Combine them into a single evaluation DataFrame.
    3. For every query, call the search engine and compare retrieved document IDs
       with the ground-truth relevant IDs using all metrics defined in
       ``evaluation_metrics.py``.
    """

    DEFAULT_K_VALUES = [1, 3, 5, 10]

    def __init__(
        self,
        search_engine: SearchEngine,
        train_path: str = TRAIN_PATH,
        test_path: str = TEST_PATH,
        k_values: Optional[List[int]] = None,
    ):
        self.search_engine = search_engine
        self.train_path = train_path
        self.test_path = test_path
        self.k_values = k_values or self.DEFAULT_K_VALUES
        self.eval_df: Optional[pd.DataFrame] = None

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def load_and_combine(self) -> pd.DataFrame:
        """Load train & test CSVs and concatenate them into one DataFrame."""
        train_df = pd.read_csv(self.train_path)
        test_df = pd.read_csv(self.test_path)

        # Drop unnamed index column if present
        for df in (train_df, test_df):
            unnamed_cols = [c for c in df.columns if c.startswith("Unnamed")]
            if unnamed_cols:
                df.drop(columns=unnamed_cols, inplace=True)

        combined = pd.concat([train_df, test_df], ignore_index=True)
        combined.drop_duplicates(subset=["qid"], inplace=True)
        combined.reset_index(drop=True, inplace=True)
        self.eval_df = combined
        print(
            f"[Evaluator] Loaded {len(train_df)} train + {len(test_df)} test "
            f"= {len(combined)} unique queries (after dedup)."
        )
        return combined

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

    # ------------------------------------------------------------------
    # Core evaluation
    # ------------------------------------------------------------------

    def evaluate(
        self,
        method: str = "bm25",
        top_n: int = 10,
        verbose: bool = True,
    ) -> Dict:
        """
        Run the full evaluation pipeline.

        Parameters
        ----------
        method : str
            Retrieval method passed to ``SearchEngine.search()``.
            One of ``'boolean'``, ``'vsm'``, ``'bm25'``.
        top_n : int
            Number of documents to retrieve per query.
        verbose : bool
            If ``True``, print progress every 100 queries.

        Returns
        -------
        dict
            A dictionary containing:
            - ``precision@k`` for each *k*
            - ``recall@k`` for each *k*
            - ``f1@k`` for each *k*
            - ``mrr`` (Mean Reciprocal Rank)
            - ``map`` (Mean Average Precision)
            - ``per_query``: list of per-query detail dicts
        """
        if self.eval_df is None:
            self.load_and_combine()

        all_retrieved: List[List[str]] = []
        all_relevant: List[List[str]] = []
        per_query_results: List[Dict] = []

        total = len(self.eval_df)
        start_time = time.time()

        for idx, row in self.eval_df.iterrows():
            query = str(row["question"])
            true_ids = self._parse_cid(row["cid"])

            # Retrieve
            try:
                results = self.search_engine.search(query, method=method, top_n=top_n)
                retrieved_ids = [str(doc_id) for doc_id, _ in results]
            except Exception as e:
                if verbose:
                    print(f"  [WARN] Query {idx} failed: {e}")
                retrieved_ids = []

            all_retrieved.append(retrieved_ids)
            all_relevant.append(true_ids)

            # Per-query metrics
            query_metrics: Dict = {"qid": row.get("qid", idx), "query": query}
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

            if verbose and (idx + 1) % 100 == 0:
                elapsed = time.time() - start_time
                print(
                    f"  [{idx + 1}/{total}] queries evaluated  "
                    f"({elapsed:.1f}s elapsed)"
                )

        elapsed_total = time.time() - start_time

        # ------------------------------------------------------------------
        # Aggregate metrics
        # ------------------------------------------------------------------
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
        aggregated["method"] = method
        aggregated["top_n"] = top_n
        aggregated["elapsed_seconds"] = round(elapsed_total, 2)
        aggregated["per_query"] = per_query_results

        if verbose:
            self._print_summary(aggregated)

        return aggregated

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _mean(values: List[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    @staticmethod
    def _print_summary(results: Dict) -> None:
        method = results["method"]
        top_n = results["top_n"]
        total = results["total_queries"]
        elapsed = results["elapsed_seconds"]

        print("\n" + "=" * 60)
        print(f"  EVALUATION RESULTS — method={method}  top_n={top_n}")
        print(f"  Total queries: {total}   Time: {elapsed}s")
        print("=" * 60)

        header = f"{'Metric':<20} {'Value':>10}"
        print(header)
        print("-" * 30)

        # Print precision / recall / f1 for each k
        for key, value in results.items():
            if key in (
                "per_query",
                "method",
                "top_n",
                "total_queries",
                "elapsed_seconds",
            ):
                continue
            print(f"  {key:<18} {value:>10.4f}")

        print("=" * 60 + "\n")

    def results_to_dataframe(self, results: Dict) -> pd.DataFrame:
        """Convert per-query results to a DataFrame for further analysis."""
        return pd.DataFrame(results["per_query"])
