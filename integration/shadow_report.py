"""Summarize a shadow log, and score it against human labels when you have them.

  python3 integration/shadow_report.py shadow.jsonl
  python3 integration/shadow_report.py shadow.jsonl --labels labels.csv   # columns: message_id,label (opt_out|not_opt_out|ambiguous)

With labels it prints recall on opt-outs, the share of non-opt-outs the system would have opted out or asked to
confirm, what happened to each true opt-out, and label counts. Label a random sample, not only the cases the model flagged.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--labels")
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.log, encoding="utf-8") if l.strip()]
    print("decisions:", len(rows))
    print("routes:", dict(Counter(r["route"] for r in rows)))
    print("sources:", dict(Counter(r["source"] for r in rows)))
    errs = [r for r in rows if r["source"] in ("error", "parse_failure")]
    print("errors or unparseable: %d (%.1f%%)" % (len(errs), 100 * len(errs) / max(1, len(rows))))
    lat = sorted(r["latency_ms"] for r in rows if r["source"] == "model")
    if lat:
        print("model latency ms p50/p95: %d / %d" % (lat[len(lat) // 2], lat[min(len(lat) - 1, int(0.95 * len(lat)))]))
    if not a.labels:
        return
    truth = {r["message_id"]: r["label"] for r in csv.DictReader(open(a.labels, encoding="utf-8"))}
    sc = [r for r in rows if r["message_id"] in truth]
    pos = [r for r in sc if truth[r["message_id"]] == "opt_out"]
    neg = [r for r in sc if truth[r["message_id"]] != "opt_out"]
    print("\nlabeled and scored:", len(sc), "(opt-outs: %d, others: %d)" % (len(pos), len(neg)))
    if pos:
        print("true opt-outs by route:", dict(Counter(r["route"] for r in pos)))
        print("recall as label: %d/%d" % (sum(r["label"] == "opt_out" for r in pos), len(pos)))
        print("true opt-outs ignored (no_action): %d" % sum(r["route"] == "no_action" for r in pos))
        old = [r for r in pos if r.get("existing_system_action") == "none"]
        print("true opt-outs the current system missed that the classifier would act on: %d of %d" % (
            sum(r["route"] in ("auto_opt_out", "send_confirmation") for r in old), len(old)))
    if neg:
        bad = [r for r in neg if r["route"] in ("auto_opt_out", "send_confirmation")]
        print("non-opt-outs it would opt out or ask to confirm: %d of %d" % (len(bad), len(neg)))
        print("non-opt-outs it would opt out automatically: %d" % sum(r["route"] == "auto_opt_out" for r in neg))


if __name__ == "__main__":
    main()
