import re
from dataclasses import dataclass

# "## Some Title { #some-anchor }" -> level, title, anchor (anchor part is optional)
HEADING = re.compile(r"^(#{1,6})\s+(.*?)(?:\s*\{\s*#([^}\s]+)\s*\})?\s*$")


@dataclass
class Section:
    level: int
    title: str
    anchor: str | None
    body: str  # text under this heading, up to the next heading


def split_sections(text: str) -> list[Section]:
    sections = []
    # text before the first heading gets a placeholder section
    current = Section(level=0, title="", anchor=None, body="")
    lines = []
    in_fence = False

    def close():
        current.body = "\n".join(lines).strip()
        sections.append(current)

    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else HEADING.match(line)
        if m:
            close()
            lines = []
            current = Section(
                level=len(m.group(1)),
                title=m.group(2).strip(),
                anchor=m.group(3),
                body="",
            )
        else:
            lines.append(line)
    close()
    return sections


if __name__ == "__main__":
    from docpilot.ingest.loader import load_docs

    docs = {d.path: d for d in load_docs()}
    doc = docs["tutorial/first-steps.md"]
    for s in split_sections(doc.text):
        print(s.level, "|", s.anchor, "|", s.title, "|", len(s.body.split()), "words")