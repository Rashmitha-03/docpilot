"""Retrieval metrics for DocPilot.

An item is a (file, anchor) pair. Gold and retrieved items use the same form.
Retrieval metrics are computed over answerable questions only.
"""
from typing import Iterable, Sequence

Section = tuple[str, str]


def recall_at_k(retrieved: Sequence[Section], gold: Iterable[Section], k: int) -> float:
    """Fraction of gold sections found in the top k retrieved items."""
    gold_set = set(gold)
    if not gold_set:
        raise ValueError("recall is undefined for a question with no gold sections")
    return len(gold_set & set(retrieved[:k])) / len(gold_set)


def reciprocal_rank(retrieved: Sequence[Section], gold: Iterable[Section]) -> float:
    """1/rank of the first retrieved item that is a gold section, else 0."""
    gold_set = set(gold)
    if not gold_set:
        raise ValueError("reciprocal rank is undefined for a question with no gold sections")
    for rank, item in enumerate(retrieved, start=1):
        if item in gold_set:
            return 1.0 / rank
    return 0.0


def evaluate(results, ks=(1, 3, 5, 10)) -> dict:
    """results: list of (retrieved, gold) pairs, one per answerable question."""
    n = len(results)
    if n == 0:
        raise ValueError("no results to evaluate")
    out = {"n": n, "mrr": sum(reciprocal_rank(r, g) for r, g in results) / n}
    for k in ks:
        out[f"recall@{k}"] = sum(recall_at_k(r, g, k) for r, g in results) / n
    return out