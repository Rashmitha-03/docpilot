# Eval format

One JSON object per line (JSONL) in `dev.jsonl` and `test.jsonl`.

| Field | Meaning |
|---|---|
| `id` | Unique, e.g. `dev-001` |
| `question` | Written by me, in my own words |
| `answerable` | `true` or `false` |
| `gold` | List of `{ "file", "anchor" }`. File is relative to `docs/en/docs/`. Empty list when `answerable` is false |

## Illustrative examples (NOT real eval data)

```json
{"id": "dev-001", "question": "Where can I see the interactive API docs?", "answerable": true, "gold": [{"file": "tutorial/first-steps.md", "anchor": "interactive-api-docs"}]}
{"id": "dev-002", "question": "How do I configure Kafka consumers?", "answerable": false, "gold": []}
```

## Rules

- Write questions from the docs' content, not by copying headings word for word.
- Unanswerable means I searched the docs and found nothing that answers it.
- A question can have more than one gold section.
- `dev.jsonl` is for tuning. `test.jsonl` is never used for tuning, only for the final reported numbers.