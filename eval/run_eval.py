import json
from pathlib import Path

import importlib
import sys

RETRIEVER = sys.argv[1] if len(sys.argv) > 1 else "vector"
search = importlib.import_module(f"docpilot.retrieval.{RETRIEVER}").search
from eval.metrics import evaluate, reciprocal_rank

DEV = Path("eval/dev.jsonl")  # DEV only. Test stays held out.
OUT = Path(f"eval/results/{RETRIEVER}_dev.json")
OVERFETCH = 30
KS = (1, 3, 5, 10)


def load_rows(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def unique_sections(hits):
    seen, out = set(), []
    for h in hits:
        key = (h.file, h.anchor)
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def main():
    rows = [r for r in load_rows(DEV) if r["answerable"]]
    results, per_q = [], []
    for r in rows:
        retrieved = unique_sections(search(r["question"], k=OVERFETCH))
        gold = [(g["file"], g["anchor"]) for g in r["gold"]]
        results.append((retrieved, gold))
        per_q.append((r["id"], reciprocal_rank(retrieved, gold)))

    scores = evaluate(results, ks=KS)
    print("questions:", len(rows))
    print("scores:", json.dumps(scores, default=str))
    for qid, rr in per_q:
        if rr < 1:
            print(f"{qid} rr={rr:.3f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(scores, indent=2, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()