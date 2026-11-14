#!/usr/bin/env bash
# Frozen v1 run: scores the held-out TEST split of both datasets with the current prompt and model.
# Run from the repo root. Needs ANTHROPIC_API_KEY unless every row is already cached.
# Each metrics.json records the prompt hash, so a changed prompt shows up as a different "v".
set -euo pipefail
python3 prototype/evaluate.py --split test --data data/replies.csv
python3 prototype/evaluate.py --split test --data data/hard_cases.csv
grep -h '"prompt_sha"' prototype/results/test/metrics.json prototype/results/hard_cases/test/metrics.json
