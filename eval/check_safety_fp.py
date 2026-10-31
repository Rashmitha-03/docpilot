import json

from docpilot.safety import pre_check

total, flagged = 0, []
for path in ("eval/dev.jsonl", "eval/test.jsonl"):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            q = row.get("question") or row.get("q") or row.get("query")
            if q is None:
                print("No question field in", path, "- keys are:", list(row))
                raise SystemExit(1)
            total += 1
            r = pre_check(q)
            if r:
                flagged.append((path, row.get("id"), r["category"], q))

print(f"{total} eval questions checked, {len(flagged)} flagged")
for item in flagged:
    print(item)