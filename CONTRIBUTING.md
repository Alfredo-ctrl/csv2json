# Contributing

csv2json is one small job: CSV and JSON tables, both ways. Keep it that way.

Rules:

- One function does one thing. Plain stdlib, no dependencies.
- Never break the JSON contract: `convert` prints the rows as JSON, errors go to stderr as `{"error": ...}`.
- A new feature touches code, test, README, MCP description and example in the same commit.
- Add a test in `tests/test_core.py` for anything new.
- Run `python -m unittest discover -s tests` before opening a PR.
- One commit per change, with a message that says why, not just what.
