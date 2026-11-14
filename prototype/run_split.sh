#!/usr/bin/env bash
# Score one split of both datasets with one prompt version. Run from the repo root.
#   prototype/run_split.sh v1 dev     # baseline on dev
#   prototype/run_split.sh v2 dev     # tune on this one
#   prototype/run_split.sh v2 test    # held-out: run ONCE per finished version
# Needs ANTHROPIC_API_KEY unless every row is already cached. Each metrics.json records the version and prompt hash.
set -euo pipefail
v="${1:?version: v1 or v2}"; split="${2:?split: dev or test}"
python3 prototype/evaluate.py --version "$v" --split "$split" --data data/replies.csv
python3 prototype/evaluate.py --version "$v" --split "$split" --data data/hard_cases.csv
