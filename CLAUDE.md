# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A product-management portfolio case study with a small working prototype. It is based on the author's real PM work at Maestra.io (a martech platform like Klaviyo/Attentive), where SMS opt-out only worked on keywords (STOP etc.), so natural-language refusals ("I don't want to receive messages from you anymore") stayed subscribed. The prototype shows an LLM catching those replies. The repo is meant to be published (GitHub plus a case study web page, later embedded in a personal portfolio site).

Ground rules for anything written here:
- All data is synthetic and all figures are labeled "illustrative assumption". Never add real Maestra numbers, client names or confidential details, and do not invent claims about what actually happened at Maestra beyond: opt-out was keyword-only, clients wrote natural-language refusals, the team wanted to handle them with AI.
- Discovery content is framed as an approach/plan, not fabricated findings or quotes.
- Prose style: plain and direct, avoiding AI-sounding patterns (run the humanizer skill over prose before finishing).

## Commands

Python 3.9 (use `from __future__ import annotations`). Install: `pip3 install -r requirements.txt`. There is no test suite or linter.

```bash
python3 data/generate_dataset.py                                   # regenerate data/replies.csv (seeded, deterministic)
python3 prototype/evaluate.py --provider mock --sample-per-category 10   # offline pipeline test, no API key
export ANTHROPIC_API_KEY=...                                       # required for real runs; never hardcode
python3 prototype/evaluate.py --provider anthropic --sample-per-category 10   # cheap real run
python3 prototype/evaluate.py --provider anthropic                 # full 450 rows
```

`--split dev|test` evaluates one split. Splits are by template family (rows are near-duplicate variants of one base phrase), about 60% dev and 40% test: tune prompts on dev, report on test once. Other flags: `--model` (default `claude-haiku-5-5`, or env `OPTOUT_MODEL`; the ID is unverified against the API), `--limit N`, `--out DIR` (default `prototype/results`), `--data PATH`.

## Architecture

- `data/replies.csv`: 450 synthetic inbound replies (columns `id,text,label,category,language,has_keyword,family,split,human_label`; labeling rules in `data/LABELING_POLICY.md`; `human_label` is the blind hand label on 70 test rows and overrides `label`. `generate_dataset.py` still produces the pre-relabel labels, so rerunning it overwrites the policy). Labels: `opt_out`, `not_opt_out`, `ambiguous`. Categories include `soft_refusal` (opt-outs with no keyword, the headline test set) and `frustrated` (angry replies with no explicit request, labeled `ambiguous`) and `keyword_trap` (contains a keyword but is not an opt-out, e.g. "cancel my order"). Languages: en, ru, es.
- `prototype/classifier.py`: keyword baseline, `llm_classify` (Anthropic Messages API, JSON output, SMS wrapped in `<sms>` tags and treated as untrusted data), `hybrid_classify` (keyword hits of 3 words or fewer are final, everything else goes to the LLM), `route()` (confidence thresholds 0.90/0.60 to `auto_opt_out` / `send_confirmation` / `human_review` / `no_action`), and `MockLLM` (offline heuristic stand-in).
- `prototype/evaluate.py`: runs keyword vs hybrid over the dataset, computes metrics, writes `metrics.json`, `metrics.md`, `threshold_sweep.png`, `recall_by_category.png`, `predictions.csv`, and `cache_<model>.json`.
- `docs/concepts.md`: running glossary of the ideas behind the project, appended as each build step is done. Add an entry whenever a new concept is introduced.
- `docs/01..08-*.md`: the PM case study (problem, discovery, PRD, risk/compliance, metrics, rollout, decision log). They must stay consistent with each other and with the code: thresholds 0.90/0.60, the 72h confirmation window and the illustrative cost figures appear across `03-prd.md`, `04-risk-and-compliance.md`, `05-metrics.md`, `06-rollout-plan.md` and `classifier.py`. Change them together.

## Things to know

- Binary metrics count `opt_out` as positive; `ambiguous` and `not_opt_out` are negative. The headline metric is recall on non-keyword opt-outs (`soft_refusal`). The keyword baseline scores about 0 there by construction, so that is a dataset-design result, not a finding.
- Mock runs write `mock_`-prefixed files in `prototype/results/` and their numbers say nothing about real model quality. Never cite them as results. Real runs write unprefixed files.
- The LLM response cache is keyed by the wrapped SMS text inside a per-model, per-prompt file. The cache file name includes a hash of `SYSTEM_PROMPT` (`cache_<model>_<sha>.json`), so editing the prompt starts a fresh cache automatically. Cache files can be gitignored.
- `llm_classify` sends no `temperature` and uses `max_tokens=60`.
- `data/hard_cases.csv` (104 hand-written adversarial English messages, built by `data/make_hard_cases.py`) is evaluated separately with `--data data/hard_cases.csv` (output in `prototype/results/hard_cases/`). Its labels were written by one person and have not been blind-checked. `prototype/run_v1.sh` scores both test splits. `metrics.md` now reports latency (p50/p95) and cost per message, using the price table in `evaluate.py` (check it before quoting).
