"""List the sections (heading level, anchor, title) of a doc file.

Usage (from repo root):
    python -m eval.list_sections tutorial/first-steps.md
The path is relative to data/fastapi_repo/docs/en/docs/.
"""
import re
import sys

from docpilot.config import settings

DOCS_ROOT = settings.data_dir / "fastapi_repo" / "docs" / "en" / "docs"
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*(?:\{\s*#([^}\s]+)\s*\})?\s*$")


def list_sections(rel_path: str):
    path = DOCS_ROOT / rel_path
    in_code = False
    sections = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith(("```", "~~~")):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = HEADING.match(line)
        if m:
            level, title, anchor = len(m.group(1)), m.group(2), m.group(3)
            sections.append((line_no, level, anchor, title))
    return sections


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m eval.list_sections <path relative to docs/en/docs>")
    secs = list_sections(sys.argv[1])
    for line_no, level, anchor, title in secs:
        print(f"{line_no:>4}  {'  ' * (level - 1)}{anchor or '(no anchor)'}  |  {title[:50]}")
    missing = sum(1 for s in secs if s[2] is None)
    print(f"\n{len(secs)} sections, {missing} without an anchor")