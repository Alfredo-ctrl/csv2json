"""Tests for csv2json. No fixtures needed, everything is built in code."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from csv2json import convert, csv_to_json, describe, json_to_csv  # noqa: E402

CSV_TEXT = "name,product,total,paid\nAna,Keyboard,120,true\nLuis,Mouse,85,true\nMia,Monitor,300,false\n"


class TestCsv2Json(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.csv = os.path.join(self.tmp, "sales.csv")
        with open(self.csv, "w", encoding="utf-8") as f:
            f.write(CSV_TEXT)

    def out(self, name):
        return os.path.join(self.tmp, name)

    def test_describe_csv(self):
        info = describe(self.csv)
        self.assertEqual(info["format"], "csv")
        self.assertEqual(info["rows"], 3)
        self.assertEqual(info["columns"], ["name", "product", "total", "paid"])
        self.assertEqual(info["delimiter"], ",")
        self.assertEqual(info["sample"][0]["name"], "Ana")

    def test_describe_semicolon(self):
        path = self.out("semi.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("a;b\n1;2\n")
        self.assertEqual(describe(path)["delimiter"], ";")

    def test_convert_types_values(self):
        result = csv_to_json(self.csv)
        self.assertEqual(result["rows"], 3)
        first = result["data"][0]
        self.assertEqual(first, {"name": "Ana", "product": "Keyboard", "total": 120, "paid": True})
        self.assertIsInstance(first["total"], int)
        self.assertIsInstance(first["paid"], bool)

    def test_convert_no_typed_keeps_strings(self):
        result = csv_to_json(self.csv, typed=False)
        self.assertEqual(result["data"][0]["total"], "120")

    def test_convert_columns_and_limit(self):
        result = csv_to_json(self.csv, columns=["name", "total"], limit=2)
        self.assertEqual(result["rows"], 2)
        self.assertEqual(result["data"][1], {"name": "Luis", "total": 85})

    def test_convert_writes_json_file(self):
        out = self.out("sales.json")
        result = csv_to_json(self.csv, output=out)
        self.assertEqual(result["output"], out)
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[2]["name"], "Mia")

    def test_convert_ndjson(self):
        out = self.out("sales.ndjson")
        csv_to_json(self.csv, output=out, ndjson=True)
        with open(out, encoding="utf-8") as f:
            lines = [json.loads(line) for line in f]
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0]["name"], "Ana")

    def test_roundtrip_json_to_csv(self):
        json_path = self.out("sales.json")
        csv_to_json(self.csv, output=json_path)
        result = json_to_csv(json_path, output=self.out("back.csv"))
        self.assertEqual(result["rows"], 3)
        self.assertEqual(result["columns"], ["name", "product", "total", "paid"])
        back = csv_to_json(self.out("back.csv"))
        self.assertEqual(back["data"][0]["name"], "Ana")
        self.assertEqual(back["data"][0]["total"], 120)

    def test_describe_json(self):
        json_path = self.out("sales.json")
        csv_to_json(self.csv, output=json_path)
        info = describe(json_path)
        self.assertEqual(info["format"], "json")
        self.assertEqual(info["rows"], 3)
        self.assertEqual(info["columns"], ["name", "product", "total", "paid"])

    def test_empty_cells_become_none(self):
        path = self.out("gaps.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("a,b\n1,\n")
        self.assertIsNone(csv_to_json(path)["data"][0]["b"])

    def test_errors(self):
        with self.assertRaises(ValueError):
            describe(self.out("nope.csv"))
        with self.assertRaises(ValueError):
            convert(self.out("nope.txt"))
        json_path = self.out("data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump([{"a": 1}], f)
        with self.assertRaises(ValueError):
            csv_to_json(json_path)
        with self.assertRaises(ValueError):
            json_to_csv(self.csv)

    def test_cli_convert_and_describe(self):
        res = subprocess.run(
            [sys.executable, "-m", "csv2json.cli", "convert", "-i", self.csv],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(json.loads(res.stdout)["rows"], 3)
        res = subprocess.run(
            [sys.executable, "-m", "csv2json.cli", "describe", "-i", self.csv],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(json.loads(res.stdout)["columns"], ["name", "product", "total", "paid"])

    def test_json_to_csv_rejects_non_dict_rows(self):
        json_path = self.out("nums.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump([1, 2, 3], f)
        with self.assertRaises(ValueError):
            json_to_csv(json_path)

    def test_mcp_smoke(self):
        env = dict(os.environ, PYTHONPATH=os.path.join(os.path.dirname(__file__), ".."))
        proc = subprocess.Popen(
            [sys.executable, "-m", "csv2json.cli", "mcp"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env=env,
        )
        try:
            reqs = [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                 "params": {"name": "describe_table", "arguments": {"input": self.csv}}},
            ]
            for req in reqs:
                proc.stdin.write(json.dumps(req) + "\n")
            proc.stdin.flush()
            lines = [proc.stdout.readline() for _ in range(3)]
            init = json.loads(lines[0])
            self.assertEqual(init["result"]["serverInfo"]["name"], "csv2json")
            tools = json.loads(lines[1])["result"]["tools"]
            self.assertIn("convert_table", [t["name"] for t in tools])
            payload = json.loads(json.loads(lines[2])["result"]["content"][0]["text"])
            self.assertEqual(payload["rows"], 3)
        finally:
            proc.stdin.close()
            proc.wait(timeout=10)


if __name__ == "__main__":
    unittest.main()
