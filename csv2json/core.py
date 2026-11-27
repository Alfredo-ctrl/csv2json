"""CSV and JSON table conversion. No dependencies, plain stdlib."""

import csv
import json
import os


def _sniff_delimiter(sample):
    try:
        return csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"]).delimiter
    except csv.Error:
        return ","


# same idea as sheetforge's _csv_value, kept separate: this one also reads true/false
def _coerce(value):
    # "42" -> 42, "3.5" -> 3.5, "true" -> True, "" -> None
    if value == "":
        return None
    low = value.lower()
    if low in ("true", "false"):
        return low == "true"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def describe(path):
    """Rows, columns, delimiter and a peek at the first rows of a .csv or .json."""
    if not os.path.exists(path):
        raise ValueError(f"file not found: {path}")
    if path.lower().endswith(".csv"):
        with open(path, newline="", encoding="utf-8-sig") as f:
            sample = f.read(4096)
            f.seek(0)
            dialect = _sniff_delimiter(sample)
            reader = csv.DictReader(f, delimiter=dialect)
            columns = reader.fieldnames or []
            rows = list(reader)
        return {
            "format": "csv",
            "path": path,
            "rows": len(rows),
            "columns": columns,
            "delimiter": dialect,
            "sample": rows[:3],
        }
    if path.lower().endswith(".json"):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            raise ValueError("JSON input must be an object or a list of objects")
        columns = list(data[0].keys()) if data and isinstance(data[0], dict) else []
        return {
            "format": "json",
            "path": path,
            "rows": len(data),
            "columns": columns,
            "delimiter": None,
            "sample": data[:3],
        }
    raise ValueError("unsupported format: only .csv and .json")


def csv_to_json(path, output=None, typed=True, columns=None, limit=None, ndjson=False):
    """Read a .csv and return a list of dicts (or write it to a .json file)."""
    if not os.path.exists(path):
        raise ValueError(f"file not found: {path}")
    if not path.lower().endswith(".csv"):
        raise ValueError("csv_to_json needs a .csv file")
    with open(path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(4096)
        f.seek(0)
        dialect = _sniff_delimiter(sample)
        reader = csv.DictReader(f, delimiter=dialect)
        header = reader.fieldnames or []
        rows = []
        for row in reader:
            if columns:
                row = {k: row.get(k) for k in columns}
            if typed:
                row = {k: _coerce(v) if isinstance(v, str) else v for k, v in row.items()}
            rows.append(row)
            if limit is not None and len(rows) >= limit:
                break
    result = {"rows": len(rows), "columns": header, "data": rows}
    if output:
        with open(output, "w", encoding="utf-8") as f:
            if ndjson:
                for row in rows:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
            else:
                json.dump(rows, f, indent=2, ensure_ascii=False)
        result["output"] = output
    return result


def json_to_csv(path, output=None, columns=None):
    """Read a .json list of objects and return rows (or write them to a .csv file)."""
    info = describe(path)
    if info["format"] != "json":
        raise ValueError("json_to_csv needs a .json file")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    if not all(isinstance(row, dict) for row in data):
        raise ValueError("json_to_csv needs a list of objects, every row has to be an object")
    cols = columns or info["columns"]
    rows = [{k: r.get(k, "") for k in cols} for r in data]
    result = {"rows": len(rows), "columns": cols, "data": rows}
    if output:
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cols)
            writer.writeheader()
            writer.writerows(rows)
        result["output"] = output
    return result


def convert(input_path, output_path=None, typed=True, columns=None, limit=None, ndjson=False):
    """Convert .csv to .json or .json to .csv. Direction follows the input."""
    if input_path.lower().endswith(".csv"):
        return csv_to_json(input_path, output_path, typed, columns, limit, ndjson)
    if input_path.lower().endswith(".json"):
        return json_to_csv(input_path, output_path, columns)
    raise ValueError("convert needs a .csv or .json file")
