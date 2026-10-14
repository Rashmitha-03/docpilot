import re
from dataclasses import dataclass

from sentence_transformers import SentenceTransformer
from docpilot.config import settings
from docpilot.ingest.loader import Doc, load_docs
from docpilot.ingest.sections import split_sections

WORD = re.compile(r"\S+")
# Terminal demos contain colour markup like <font color="#4E9A06">...</font>.
# It costs many tokens and carries no meaning, so we strip it before chunking.
MARKUP = re.compile(r"</?(?:font|span|u|div)\b[^>]*>")
MAX_TOKENS = 400  # starting guess; bge-small reads 512 max, minus header and special tokens
_tok = SentenceTransformer(settings.embed_model).tokenizer

def n_tokens(text: str) -> int:
    return len(_tok.encode(text, add_special_tokens=False))

def cap_tokens(piece: str, header: str, size: int, overlap: int) -> list[str]:
    """Split a piece again (fewer words each time) until header + piece fits MAX_TOKENS."""
    if n_tokens(header + "\n\n" + piece) <= MAX_TOKENS or size <= 10:
        return [piece]
    out = []
    for p in split_words(piece, size // 2, min(overlap, size // 4)):
        out.extend(cap_tokens(p, header, size // 2, overlap))
    return out


def clean(text: str) -> str:
    return MARKUP.sub("", text)

@dataclass
class Chunk:
    id: str
    file: str
    anchor: str | None
    header: str  # e.g. "First Steps > Check it"
    text: str  # header + body piece: this is what gets embedded

def split_words(body: str, size: int, overlap: int) -> list[str]:
    """Cut body into pieces of at most `size` words, sharing `overlap` words."""
    words = list(WORD.finditer(body))
    if len(words) <= size:
        return [body]
    pieces, start = [], 0
    while True:
        end = min(start + size, len(words))
        pieces.append(body[words[start].start() : words[end - 1].end()])
        if end == len(words):
            break
        start = end - overlap
    return pieces


def chunk_doc(doc: Doc) -> list[Chunk]:
    chunks = []
    stack = []  # (level, title) of the headings above the current section
    for i, s in enumerate(split_sections(doc.text)):
        if s.level == 0:
            continue
        while stack and stack[-1][0] >= s.level:
            stack.pop()
        stack.append((s.level, s.title))
        if not s.body:
            continue  # empty section: still part of the header path, but no chunk
        header = " > ".join(t for _, t in stack)
        pieces = []
        for p in split_words(clean(s.body), settings.chunk_size, settings.chunk_overlap):
            pieces.extend(cap_tokens(p, header, settings.chunk_size, settings.chunk_overlap))
        for j, piece in enumerate(pieces):
            chunks.append(
                Chunk(
                    id=f"{doc.path}::{i}::{j}",
                    file=doc.path,
                    anchor=s.anchor,
                    header=header,
                    text=header + "\n\n" + piece,
                )
            )
    return chunks


if __name__ == "__main__":
    all_chunks = []
    for d in load_docs():
        all_chunks.extend(chunk_doc(d))
    print("chunks:", len(all_chunks))
    print("from split sections:", sum(1 for c in all_chunks if not c.id.endswith("::0")))
    for c in all_chunks:
        if c.file == "tutorial/first-steps.md" and c.anchor == "interactive-api-docs":
            print("id:", c.id)
            print("anchor:", c.anchor)
            print("header:", c.header)
            print("text:", c.text[:300])