from dataclasses import dataclass
from pathlib import Path

DOCS_ROOT = Path("data/fastapi_repo/docs/en/docs")

# Files left out of the index. release-notes.md is a ~56k-word changelog (about
# 34% of the corpus) that mentions many feature names but explains none of them.
EXCLUDE = {"release-notes.md"}


@dataclass
class Doc:
    path: str  # relative to DOCS_ROOT, with forward slashes (matches gold labels)
    text: str


def load_docs(root: Path = DOCS_ROOT) -> list[Doc]:
    docs = []
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root).as_posix()
        if rel in EXCLUDE:
            continue
        text = p.read_text(encoding="utf-8")
        docs.append(Doc(path=rel, text=text))
    return docs


if __name__ == "__main__":
    docs = load_docs()
    print("files:", len(docs))
    print("words:", sum(len(d.text.split()) for d in docs))
    print("--- 8 largest ---")
    by_size = sorted(docs, key=lambda d: len(d.text.split()), reverse=True)
    for d in by_size[:8]:
        print(len(d.text.split()), d.path)