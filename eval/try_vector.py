import sys

from docpilot.retrieval.vector import search

q = " ".join(sys.argv[1:])
for i, h in enumerate(search(q), 1):
    print(f"{i}. {h.score:.3f} | {h.file} #{h.anchor or '-'} | {h.header}")