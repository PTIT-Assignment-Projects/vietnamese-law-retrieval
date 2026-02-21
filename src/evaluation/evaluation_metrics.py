from typing import List, Iterable


def calculate_precision_at_k(retrieved_ids: List[str], true_ids: List[str], k) -> float:
    if k == 0:
        return 0.0
    k_retrieved = retrieved_ids[:k]
    hits = len([rid for rid in k_retrieved if rid in true_ids])
    return hits / k
def calculate_recall_at_k(retrieved_ids: List[str], true_ids: List[str], k) -> float:
    if not true_ids:
        return 0.0
    k_retrieved = retrieved_ids[:k]
    hits = len([rid for rid in k_retrieved if rid in true_ids])
    return hits / len(true_ids)
def calculate_f1_at_k(retrieved_ids: List[str], true_ids: List[str], k: int) -> float:
    if not true_ids or k <= 0:
        return 0.0
    precision = calculate_precision_at_k(retrieved_ids, true_ids, k)
    recall = calculate_recall_at_k(retrieved_ids, true_ids, k)
    if precision + recall == 0.0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)
def reciprocal_rank(retrieved_ids: List[str], true_ids: Iterable[str]) -> float:
    relevant_set = set(true_ids)
    for i, doc in enumerate(retrieved_ids, start = 1):
        if doc in relevant_set:
            return 1.0 / i
    return 0.0
def mean_reciprocal_rank(retrieved_ids: List[List[str]], true_ids: List[Iterable[str]]) -> float:
    if not retrieved_ids:
        return 0.0
    rr_values = [
        reciprocal_rank(r, rel)
        for r, rel in zip(retrieved_ids, true_ids)
    ]
    return sum(rr_values) / len(rr_values)
def calculate_average_precision(retrieved_ids: List[str], true_ids: List[str]) -> float:
    if not true_ids:
        return 0.0
    average_precision = 0.0
    hits = 0
    for i, rid in enumerate(retrieved_ids):
        if rid in true_ids:
            hits += 1
            average_precision += hits / (i + 1)
    return average_precision / len(true_ids)