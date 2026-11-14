"""Fix the final labels of data/fresh_cases.csv BEFORE any classifier is scored on it.

Rule: the blind human label wins where it exists (25 rows). Otherwise the label stands only if the author's intent and the
judge agree (`consensus`). Where they differ and there is no human label, the row is `disputed`: its `label` is left empty
and evaluate.py skips it. The original intent stays in `author_label`.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
judge = {r["id"]: r["judge_label"] for r in csv.DictReader(open(ROOT / "prototype/results/judge/policy_fresh_cases_predictions.csv", encoding="utf-8"))}
path = ROOT / "data/fresh_cases.csv"
data = list(csv.DictReader(open(path, encoding="utf-8")))
for r in data:
    a, j, h = r["author_label"], judge[r["id"]], r["human_label"]
    r["judge_label"] = j
    if h:
        r["label"], r["label_source"] = h, "human"
    elif a == j:
        r["label"], r["label_source"] = a, "consensus"
    else:
        r["label"], r["label_source"] = "", "disputed"
cols = list(data[0])
with open(path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(data)
from collections import Counter
print(Counter(r["label_source"] for r in data), Counter(r["label"] for r in data))
print("disputed:", [(r["id"], r["text"], r["author_label"], r["judge_label"]) for r in data if r["label_source"] == "disputed"])
