"""MCP server over stdio. Hand-rolled JSON-RPC, no MCP SDK.

Tools: convert_table, describe_table.
"""

import json
import sys

from . import __version__, convert, describe

TOOLS = [
    {
        "name": "convert_table",
        "description": "Convert a .csv file to .json or a .json file to .csv. Direction follows the input file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "Input .csv or .json path"},
                "output": {"type": "string", "description": "Output path. Omit to get the rows back as JSON."},
                "typed": {"type": "boolean", "description": "Convert numbers and booleans from strings (default true)", "default": True},
                "columns": {"type": "array", "items": {"type": "string"}, "description": "Keep only these columns, in this order"},
                "limit": {"type": "integer", "description": "Convert at most this many rows"},
                "ndjson": {"type": "boolean", "description": "Write one JSON object per line instead of an array", "default": False},
            },
            "required": ["input"],
        },
    },
    {
        "name": "describe_table",
        "description": "Get rows, columns, delimiter and a sample of a .csv or .json table.",
        "inputSchema": {
            "type": "object",
            "properties": {"input": {"type": "string", "description": "Table path"}},
            "required": ["input"],
        },
    },
]


def _text_result(payload):
    return {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}]}


def _dispatch_tool(name, args):
    if name == "convert_table":
        return _text_result(convert(
            args["input"],
            args.get("output"),
            typed=args.get("typed", True),
            columns=args.get("columns"),
            limit=args.get("limit"),
            ndjson=args.get("ndjson", False),
        ))
    if name == "describe_table":
        return _text_result(describe(args["input"]))
    raise ValueError(f"unknown tool '{name}'")


def run():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = req.get("method", "")
        req_id = req.get("id")
        if method in ("notifications/initialized", "notifications/cancelled"):
            continue
        if method == "initialize":
            result = {
                "protocolVersion": req.get("params", {}).get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "csv2json", "version": __version__},
            }
            resp = {"result": result}
        elif method == "ping":
            resp = {"result": {}}
        elif method == "tools/list":
            resp = {"result": {"tools": TOOLS}}
        elif method == "tools/call":
            try:
                resp = {"result": _dispatch_tool(req["params"]["name"], req["params"].get("arguments", {}))}
            except Exception as e:
                resp = {"result": {"content": [{"type": "text", "text": json.dumps({"error": str(e)})}], "isError": True}}
        else:
            resp = {"error": {"code": -32601, "message": f"method not found: {method}"}}
        if req_id is not None:
            print(json.dumps({"jsonrpc": "2.0", "id": req_id, **resp}), flush=True)
