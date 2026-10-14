from sentence_transformers import SentenceTransformer

from docpilot.ingest.loader import load_docs
from docpilot.ingest.sections import split_sections

tok = SentenceTransformer("BAAI/bge-small-en-v1.5").tokenizer

toks, words = [], []
for d in load_docs():
    for s in split_sections(d.text):
        if s.level == 0 or not s.body:
            continue
        text = s.title + "\n" + s.body
        toks.append(len(tok.encode(text, add_special_tokens=True)))
        words.append(len(text.split()))

toks_sorted = sorted(toks)
n = len(toks_sorted)
print("sections (non-empty):", n)
print("tokens per word:", round(sum(toks) / sum(words), 2))
print("median tokens:", toks_sorted[n // 2])
print("p90 tokens:", toks_sorted[int(n * 0.9)])
print("p99 tokens:", toks_sorted[int(n * 0.99)])
print("max tokens:", toks_sorted[-1])
print("over 300 tokens:", sum(1 for t in toks if t > 300))
print("over 512 tokens:", sum(1 for t in toks if t > 512))