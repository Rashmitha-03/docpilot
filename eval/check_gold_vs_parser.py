import json
from pathlib import Path

from docpilot.ingest.loader import load_docs
from docpilot.ingest.sections import split_sections

# every (file, anchor) the parser can produce
found = set()
for d in load_docs():
    for s in split_sections(d.text):
        if s.anchor:
            found.add((d.path, s.anchor))

checked = 0
missing = 0
for name in ["eval/dev.jsonl", "eval/test.jsonl"]:
    for line in Path(name).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for g in row.get("gold", []):
            checked += 1
            if (g["file"], g["anchor"]) not in found:
                missing += 1
                print("MISSING:", row["id"], g["file"], g["anchor"])

print("gold labels checked:", checked)
print("gold labels not found in parser output:", missing)