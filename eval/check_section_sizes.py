from docpilot.ingest.loader import load_docs
from docpilot.ingest.sections import split_sections

sizes = []
for d in load_docs():
    for s in split_sections(d.text):
        if s.level > 0:
            sizes.append(len(s.body.split()))

sizes.sort()
n = len(sizes)
print("sections:", n)
print("empty (0 words):", sum(1 for x in sizes if x == 0))
print("under 30 words:", sum(1 for x in sizes if x < 30))
print("median:", sizes[n // 2])
print("p90:", sizes[int(n * 0.9)])
print("p99:", sizes[int(n * 0.99)])
print("max:", sizes[-1])
print("over 200 words:", sum(1 for x in sizes if x > 200))
print("over 400 words:", sum(1 for x in sizes if x > 400))