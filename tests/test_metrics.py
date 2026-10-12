import pytest

from eval.metrics import evaluate, recall_at_k, reciprocal_rank

A, B, X, Y = ("f.md", "a"), ("f.md", "b"), ("f.md", "x"), ("f.md", "y")


def test_recall_single_gold():
    assert recall_at_k([X, A, Y], [A], 1) == 0.0
    assert recall_at_k([X, A, Y], [A], 2) == 1.0


def test_recall_multi_gold():
    retrieved = [A, X, B]
    assert recall_at_k(retrieved, [A, B], 1) == 0.5
    assert recall_at_k(retrieved, [A, B], 2) == 0.5
    assert recall_at_k(retrieved, [A, B], 3) == 1.0


def test_recall_duplicates_do_not_inflate():
    assert recall_at_k([A, A, A], [A, B], 3) == 0.5


def test_reciprocal_rank():
    assert reciprocal_rank([X, Y, B], [B]) == pytest.approx(1 / 3)
    assert reciprocal_rank([X, B, A], [A, B]) == 0.5


def test_no_hit_is_zero():
    assert recall_at_k([X, Y], [A], 2) == 0.0
    assert reciprocal_rank([X, Y], [A]) == 0.0


def test_empty_gold_raises():
    with pytest.raises(ValueError):
        recall_at_k([A], [], 1)
    with pytest.raises(ValueError):
        reciprocal_rank([A], [])


def test_evaluate_averages():
    results = [([A, X], [A]), ([X, A], [A])]
    out = evaluate(results, ks=(1, 3))
    assert out["n"] == 2
    assert out["mrr"] == pytest.approx(0.75)
    assert out["recall@1"] == pytest.approx(0.5)
    assert out["recall@3"] == pytest.approx(1.0)