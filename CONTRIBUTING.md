# Contributing

csv2json is small on purpose. It converts tables both ways and stays out of the way.

Rules:

- No new dependencies. Everything is stdlib.
- Never break the JSON contract: `csv2json describe` and `csv2json convert` must keep printing the same shape.
- Add a test in `tests/test_core.py` for any new behavior.
- Run `python -m unittest` before opening a PR.

That's it.
