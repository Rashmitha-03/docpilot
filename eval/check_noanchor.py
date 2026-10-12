import json
from collections import Counter
from pathlib import Path

from docpilot.ingest.loader import load_docs
from docpilot.ingest.sections import split_sections

# 1) which files have headings without an anchor
counts = Counter()
for d in load_docs():
    for s in split_sections(d.text):
        if s.level > 0 and s.anchor is None:
            counts[d.path] += 1
print("--- files with no-anchor headings ---")
for path, n in counts.most_common():
    print(n, path)

# 2) do any gold labels look like a missing anchor?
print("--- gold rows (answerable) with an empty/missing anchor ---")
bad = 0
for name in ["eval/dev.jsonl", "eval/test.jsonl"]:
    for line in Path(name).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        text = json.dumps(row)
        if '"anchor": null' in text or '"anchor": ""' in text:
            bad += 1
            print("GOLD:", name, row.get("id"))
print("gold rows with empty anchor:", bad)