"""Copy the blind hand labels from data/handlabel/fresh_blind_sample.csv into data/fresh_cases.csv (human_label).

Skips the stray title line a spreadsheet app may add above the header. Run before judging; the judge never sees
the column, it is only used to compute agreement afterwards.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = list(csv.reader(open(ROOT / "data/handlabel/fresh_blind_sample.csv", encoding="utf-8-sig")))
h = next(i for i, r in enumerate(rows) if r and r[0].strip() == "id")
hdr = rows[h]
human = {r[hdr.index("id")].strip(): r[hdr.index("your_label")].strip() for r in rows[h + 1:] if r}
assert all(v in ("opt_out", "not_opt_out", "ambiguous") for v in human.values()), "bad label value"
path = ROOT / "data/fresh_cases.csv"
data = list(csv.DictReader(open(path, encoding="utf-8")))
for r in data:
    r["human_label"] = human.get(r["id"], "")
with open(path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(data[0]))
    w.writeheader()
    w.writerows(data)
print("human labels merged:", sum(1 for r in data if r["human_label"]))
