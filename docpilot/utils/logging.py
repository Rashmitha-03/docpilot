import json
import time
from pathlib import Path

LOG = Path("logs/requests.jsonl")


def log_request(**fields):
    """Append one JSON line. Never raises: logging must not break a request."""
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), **fields}
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass