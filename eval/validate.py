"""Validate an eval JSONL file against the docs.

Usage (from repo root):
    python -m eval.validate eval/dev.jsonl
    python -m eval.validate eval/dev.jsonl --show dev-005
"""
import json
import sys

from eval.list_sections import DOCS_ROOT, list_sections

REQUIRED = {"id", "question", "answerable", "gold"}


def load(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if line.strip():
                rows.append((line_no, json.loads(line)))
    return rows


def section_text(file, anchor, max_lines=20):
    secs = list_sections(file)
    lines = (DOCS_ROOT / file).read_text(encoding="utf-8").splitlines()
    for i, (line_no, _level, a, _title) in enumerate(secs):
        if a == anchor:
            end = secs[i + 1][0] - 1 if i + 1 < len(secs) else len(lines)
            return lines[line_no - 1:end][:max_lines]
    return None


def validate(path):
    errors, seen_ids, anchor_cache = [], set(), {}
    rows = load(path)
    for line_no, row in rows:
        where = f"line {line_no} ({row.get('id', '?')})"
        missing = REQUIRED - row.keys()
        if missing:
            errors.append(f"{where}: missing fields {sorted(missing)}")
            continue
        if row["id"] in seen_ids:
            errors.append(f"{where}: duplicate id")
        seen_ids.add(row["id"])
        if not isinstance(row["answerable"], bool):
            errors.append(f"{where}: 'answerable' must be true or false")
        if row["answerable"] and not row["gold"]:
            errors.append(f"{where}: answerable but gold is empty")
        if not row["answerable"] and row["gold"]:
            errors.append(f"{where}: unanswerable but gold is not empty")
        for g in row["gold"]:
            f, a = g.get("file"), g.get("anchor")
            if not (DOCS_ROOT / str(f)).is_file():
                errors.append(f"{where}: file not found: {f}")
                continue
            if f not in anchor_cache:
                anchor_cache[f] = {s[2] for s in list_sections(f)}
            if a not in anchor_cache[f]:
                errors.append(f"{where}: anchor '{a}' not found in {f}")
    n_ans = sum(1 for _, r in rows if r.get("answerable") is True)
    print(f"{len(rows)} rows ({n_ans} answerable, {len(rows) - n_ans} unanswerable)")
    return errors


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit("Usage: python -m eval.validate <file.jsonl> [--show <id>]")
    if "--show" in args:
        target = args[args.index("--show") + 1]
        for _, row in load(args[0]):
            if row["id"] == target:
                print("Q:", row["question"])
                for g in row["gold"]:
                    print(f"\n--- {g['file']} #{g['anchor']} ---")
                    print("\n".join(section_text(g["file"], g["anchor"]) or ["(not found)"]))
        sys.exit()
    errs = validate(args[0])
    print("\n".join(errs) if errs else "no problems found")