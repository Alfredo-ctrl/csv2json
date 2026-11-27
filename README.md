# csv2json

CSV and JSON tables, both ways. No dependencies, plain stdlib.

## Install

```sh
pip install git+https://github.com/Alfredo-ctrl/csv2json.git
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
{"rows": 3, "columns": ["name", "product", "total", "paid"], "data": [{"name": "Ana", "product": "Keyboard", "total": 120, "paid": true}, {"name": "Luis", "product": "Mouse", "total": 85, "paid": true}, {"name": "Mia", "product": "Monitor", "total": 300, "paid": false}], "output": "sales.json"}
```

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

See [LICENSE](LICENSE).
