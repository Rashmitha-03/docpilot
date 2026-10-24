# Corpus manifest

| Field | Value |
|---|---|
| Corpus | FastAPI documentation (English, Markdown) |
| Source | https://github.com/fastapi/fastapi |
| Path used | `docs/en/docs/**/*.md` |
| Pinned commit | `f5c6e9b` |
| Downloaded | 2026-10-11 |
| Markdown files | 156 (tutorial 51, advanced 35, reference 24, top-level 22, how-to 12, deployment 9, about 1, learn 1, resources 1) |
| Corpus size | about 166,270 words (measured with PowerShell `Measure-Object -Word`) |
| Licence | MIT (Copyright (c) 2018 Sebastián Ramírez) |
| Local copy | `data/fastapi_repo/` (gitignored, re-create with `git clone` + checkout of the pinned commit) |

## Scope notes

- English docs only. Translations are excluded.
- Source repo files outside `docs/en/docs` (code, tests, other languages) are not indexed.
- Chosen because the docs are narrow, well-structured by headings, and self-contained, which makes hand-labelling eval questions practical.

## Attribution

Documentation text belongs to the FastAPI authors and is used under the MIT licence. The licence text is in `data/fastapi_repo/LICENSE`.

## Structure notes (seen in `tutorial/first-steps.md`, verify on other files in M3)

- Headings carry an anchor suffix, e.g. `# First Steps { #first-steps }`.
- Code examples are include markers like `{* ../../docs_src/first_steps/tutorial001_py310.py *}`, so the code is not in the indexed text.
- Heading levels can skip (a `#` followed directly by `###`)