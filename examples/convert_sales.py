"""Turn a small sales CSV into JSON and print the summary."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from csv2json import convert, describe  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    csv_path = os.path.join(tmp, "sales.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("name,product,total,paid\nAna,Keyboard,120,true\nLuis,Mouse,85,true\nMia,Monitor,300,false\n")

    print(describe(csv_path))
    out = convert(csv_path, os.path.join(tmp, "sales.json"))
    print(out["rows"], "rows converted")
    print(out["data"][0])
