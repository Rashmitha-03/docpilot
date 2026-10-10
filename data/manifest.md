# Corpus manifest

| Field | Value |
|---|---|
| Corpus | FastAPI documentation (English, Markdown) |
| Source | https://github.com/fastapi/fastapi |
| Path used | `docs/en/docs/**/*.md` |
| Pinned commit | `f5c6e9b` |
| Downloaded | 2026-10-11 |
| Markdown files | 156 |
| Licence | MIT (Copyright (c) 2018 Sebastián Ramírez) |
| Local copy | `data/fastapi_repo/` (gitignored, re-create with `git clone` + checkout of the pinned commit) |

## Scope notes

- English docs only. Translations are excluded.
- Source repo files outside `docs/en/docs` (code, tests, other languages) are not indexed.
- Chosen because the docs are narrow, well-structured by headings, and self-contained, which makes hand-labelling eval questions practical.

## Attribution

Documentation text belongs to the FastAPI authors and is used under the MIT licence. The licence text is in `data/fastapi_repo/LICENSE`.