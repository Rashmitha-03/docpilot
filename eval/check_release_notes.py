import json
from pathlib import Path

hits = 0
for name in ["eval/dev.jsonl", "eval/test.jsonl"]:
    for line in Path(name).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if "release-notes" in json.dumps(row):
            hits += 1
            print("HIT:", name, row.get("id"))
print("total hits:", hits)