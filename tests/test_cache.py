from docpilot.utils.cache import LRUCache, make_key


def test_key_normalises_case_and_whitespace():
    assert make_key("  What IS   X? ", "naive") == make_key("what is x?", "naive")


def test_key_separates_modes():
    assert make_key("what is x?", "naive") != make_key("what is x?", "agent")


def test_evicts_least_recently_used():
    c = LRUCache(max_size=2)
    c.set("a", 1)
    c.set("b", 2)
    c.get("a")
    c.set("c", 3)
    assert c.get("b") is None
    assert c.get("a") == 1
    assert len(c) == 2


def test_hit_and_miss_counters():
    c = LRUCache(max_size=2)
    c.set("a", 1)
    c.get("a")
    c.get("zzz")
    assert (c.hits, c.misses) == (1, 1)