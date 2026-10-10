# DocPilot

A citation-first RAG assistant that answers questions over a narrow documentation corpus, cites the exact file and section, and refuses when the docs don't cover the question.

**Status:** in development (M0: foundation)

## Results

All numbers come from my own eval runs. Blanks mean "not measured yet".

| Config | recall@k | MRR |
|---|---|---|
| Vector only | | |
| BM25 only | | |
| Hybrid (RRF) | | |
| Hybrid + rerank | | |

## Setup

```powershell
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m docpilot.config
```

## Design decisions

_To be written as the project grows._

## Limitations

_To be written as the project grows._