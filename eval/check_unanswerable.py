"""For each unanswerable dev question, count doc files containing its distinctive words.

Usage (from repo root):
    python -m eval.check_unanswerable eval/dev.jsonl
"""
import re
import sys

from eval.list_sections import DOCS_ROOT
from eval.validate import load

STOP = {
    "that", "with", "from", "this", "have", "what", "which", "when", "does",
    "your", "each", "into", "they", "them", "then", "than", "there", "about",
    "would", "should", "could", "make", "using", "used", "need", "want",
    "give", "take", "docs", "fastapi", "where", "will", "can", "the", "how",
}


def main(path):
    texts = {
        p.relative_to(DOCS_ROOT).as_posix(): p.read_text(encoding="utf-8").lower()
        for p in DOCS_ROOT.rglob("*.md")
    }
    for _, row in load(path):
        if row["answerable"]:
            continue
        print(f"\n{row['id']}: {row['question']}")
        words = sorted({
            w for w in re.findall(r"[a-z][a-z0-9\-]+", row["question"].lower())
            if len(w) >= 4 and w not in STOP
        })
        for w in words:
            files = [f for f, t in texts.items() if w in t]
            where = ", ".join(files[:3]) if 0 < len(files) <= 3 else ""
            print(f"  {w:<16}{len(files):>4} files  {where}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m eval.check_unanswerable <file.jsonl>")
    main(sys.argv[1])