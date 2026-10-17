from docpilot.agent.nodes import verify

SRC = [{"n": 1}, {"n": 2}]


def test_empty():
    assert verify("  ", SRC, False) == ["empty"]


def test_valid_citation():
    assert verify("Use Query [1] and [2].", SRC, False) == []


def test_bad_citation():
    assert verify("See [3].", SRC, False) == ["bad_citation"]


def test_no_citation():
    assert verify("Use Query.", SRC, False) == ["no_citation"]


def test_refused_skips_checks():
    assert verify("I could not find this in the FastAPI docs.", [], True) == []