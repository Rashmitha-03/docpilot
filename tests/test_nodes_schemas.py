from docpilot.agent.nodes import grade, route
from docpilot.api.schemas import AskRequest
from docpilot.thresholds import CE_THRESHOLD


def test_route_chitchat():
    assert route("thanks") == "chitchat"
    assert route("Hello there!") == "chitchat"
    assert route("") == "chitchat"


def test_route_docs():
    assert route("How do I declare a query parameter?") == "docs"
    assert route("thanks, but how do I add CORS?") == "docs"


def test_grade_bands():
    assert grade(CE_THRESHOLD) == "strong"
    assert grade(CE_THRESHOLD - 0.01) == "weak"
    assert grade(0.0) == "weak"
    assert grade(-0.01) == "hopeless"


def test_history_dicts_become_tuples():
    req = AskRequest(question="q", history=[{"role": "user", "content": "hi"}])
    assert req.history == [("user", "hi")]


def test_history_pairs_pass_through():
    req = AskRequest(question="q", history=[["user", "hi"]])
    assert req.history == [("user", "hi")]


def test_mode_validated():
    try:
        AskRequest(question="q", mode="bogus")
    except ValueError:
        return
    raise AssertionError("bad mode accepted")