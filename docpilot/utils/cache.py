"""Small in-memory LRU cache (least recently used items are dropped first)."""
from collections import OrderedDict
from threading import Lock


def make_key(question: str, mode: str) -> str:
    """Normalise so 'What is X?' and '  what is   x? ' share one entry."""
    return mode + "|" + " ".join(question.lower().split())


class LRUCache:
    def __init__(self, max_size: int = 128):
        self.max_size = max_size
        self._data = OrderedDict()
        self._lock = Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        with self._lock:
            if key in self._data:
                self._data.move_to_end(key)
                self.hits += 1
                return self._data[key]
            self.misses += 1
            return None

    def set(self, key, value):
        with self._lock:
            self._data[key] = value
            self._data.move_to_end(key)
            while len(self._data) > self.max_size:
                self._data.popitem(last=False)

    def __len__(self):
        return len(self._data)