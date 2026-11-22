# csv2json

CSV and JSON tables, both ways, for AI agents. No GUI, no account, no dependencies: a CLI, a Python API and an MCP server that any agent can drive — Muse, Antigravity, Codex, Claude Code, or a local model.

## Install

```sh
pip install csv2json
```

## Use it from the terminal

```sh
# what does this file look like?
csv2json describe -i sales.csv

# convert it, numbers and booleans typed
csv2json convert -i sales.csv -o sales.json

# only two columns, first 10 rows, one object per line
csv2json convert -i sales.csv -o top.json --columns name total --limit 10 --ndjson

# back to csv
csv2json convert -i sales.json -o sales.csv
```

Output is JSON, so it is easy to parse:

```json
{"rows": 3, "columns": ["name", "total"], "data": [{"name": "Ana", "total": 120}, {"name": "Luis", "total": 85}]}
```

## How an agent uses it

You translate the user's words into a conversion. `csv2json describe` tells you the columns, the delimiter and a sample, so there is nothing to guess. Examples:

- "turn this spreadsheet into JSON" -> convert
- "just give me the name and price columns" -> convert with --columns
- "is this csv semicolon-separated?" -> describe

## Use it from Python

```python
from csv2json import convert, describe

print(describe("sales.csv")["columns"])
print(convert("sales.csv", "sales.json", columns=["name", "total"])["rows"])
```

## MCP server

Any MCP client can use csv2json as tools:

```sh
csv2json mcp
```

It speaks MCP over stdio and exposes `convert_table` and `describe_table`. Example client config:

```json
{
  "mcpServers": {
    "csv2json": {"command": "csv2json", "args": ["mcp"]}
  }
}
```

## License

MIT
