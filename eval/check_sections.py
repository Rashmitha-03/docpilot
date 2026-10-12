from docpilot.ingest.loader import load_docs
from docpilot.ingest.sections import split_sections

docs = load_docs()
total = 0
no_anchor = []
for d in docs:
    for s in split_sections(d.text):
        if s.level == 0:
            continue
        total += 1
        if s.anchor is None:
            no_anchor.append((d.path, s.title))

print("files:", len(docs))
print("headings:", total)
print("without anchor:", len(no_anchor))
for path, title in no_anchor[:10]:
    print("NOANCHOR:", path, "|", title)