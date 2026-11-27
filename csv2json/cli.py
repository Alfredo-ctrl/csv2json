"""csv2json command line. JSON in, JSON out."""

import argparse
import json
import sys

from . import __version__, convert, describe


def _exit_error(msg):
    print(json.dumps({"error": msg}), file=sys.stderr)
    raise SystemExit(1)


def _print_result(payload):
    print(json.dumps(payload, ensure_ascii=False))


def cmd_convert(args):
    try:
        result = convert(
            args.input,
            args.output,
            typed=not args.no_typed,
            columns=args.columns,
            limit=args.limit,
            ndjson=args.ndjson,
        )
    except (ValueError, OSError) as e:
        _exit_error(str(e))
    _print_result(result)


def cmd_describe(args):
    try:
        result = describe(args.input)
    except (ValueError, OSError) as e:
        _exit_error(str(e))
    _print_result(result)


def cmd_mcp(args):
    from .mcp_server import run

    run()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="csv2json", description="Convert CSV and JSON tables, both ways.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_conv = sub.add_parser("convert", help="Convert a .csv to .json or a .json to .csv.")
    p_conv.add_argument("-i", "--input", required=True, help="Input .csv or .json file")
    p_conv.add_argument("-o", "--output", default=None, help="Output file. Prints JSON to stdout if omitted.")
    p_conv.add_argument("--columns", nargs="+", default=None, help="Keep only these columns, in this order")
    p_conv.add_argument("--limit", type=int, default=None, help="Convert at most this many rows")
    p_conv.add_argument("--ndjson", action="store_true", help="Write one JSON object per line instead of an array")
    p_conv.add_argument("--no-typed", action="store_true", help="Keep every value a string, no number/bool conversion")
    p_conv.set_defaults(func=cmd_convert)

    p_desc = sub.add_parser("describe", help="Print rows, columns, delimiter and a sample as JSON.")
    p_desc.add_argument("-i", "--input", required=True, help="Input .csv or .json file")
    p_desc.set_defaults(func=cmd_describe)

    p_mcp = sub.add_parser("mcp", help="Start the MCP server on stdio.")
    p_mcp.set_defaults(func=cmd_mcp)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
