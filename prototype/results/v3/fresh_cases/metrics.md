# Opt-out classifier evaluation

Provider: `anthropic`, model: `claude-haiku-5-5`, rows evaluated: 63, LLM parse failures: 0

Binary metrics: opt_out is positive; ambiguous and not_opt_out both count as negative.

## Overall (opt_out)

| method | precision | recall | F1 | headline recall (soft_refusal) | FPR on keyword_trap |
|---|---|---|---|---|---|
| keyword | 0.600 | 0.265 | 0.367 | 0.250 (n=12) | 1.000 (n=5) |
| hybrid | 1.000 | 0.882 | 0.938 | 1.000 (n=12) | 0.000 (n=5) |

## Recall by opt_out category

| category | keyword | hybrid |
|---|---|---|
| account | 0.667 | 1.000 |
| blunt_refusal | 0.200 | 1.000 |
| buried_request | 0.333 | 0.333 |
| channel_switch | 0.000 | 1.000 |
| frustrated | 0.000 | 0.000 |
| prompt_injection | 0.333 | 0.333 |
| sarcasm | 0.000 | 0.333 |
| soft_refusal | 0.250 | 1.000 |
| third_party | 0.500 | 1.000 |
| typo_keyword | 0.000 | 1.000 |
| wrong_number | 0.000 | 0.000 |

## Label accuracy by category (predicted label equals true label)

| category | n | keyword | hybrid |
|---|---|---|---|
| account | 3 | 2/3 | 3/3 |
| blunt_refusal | 5 | 1/5 | 5/5 |
| buried_request | 3 | 2/3 | 2/3 |
| channel_switch | 2 | 0/2 | 2/2 |
| deferral | 4 | 4/4 | 4/4 |
| frustrated | 4 | 0/4 | 3/4 |
| keyword_trap | 5 | 0/5 | 5/5 |
| partial_scope | 3 | 0/3 | 3/3 |
| positive | 4 | 4/4 | 4/4 |
| prompt_injection | 3 | 3/3 | 3/3 |
| question | 4 | 3/4 | 4/4 |
| sarcasm | 3 | 0/3 | 3/3 |
| soft_refusal | 12 | 3/12 | 12/12 |
| third_party | 2 | 1/2 | 2/2 |
| typo_keyword | 3 | 0/3 | 3/3 |
| wrong_number | 3 | 0/3 | 1/3 |

## By language

| method | lang | n | precision | recall | F1 |
|---|---|---|---|---|---|
| keyword | en | 63 | 0.600 | 0.265 | 0.367 |
| hybrid | en | 63 | 1.000 | 0.882 | 0.938 |

## Confusion matrix: keyword (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 9 | 25 | 0 |
| not_opt_out | 6 | 14 | 0 |
| ambiguous | 0 | 9 | 0 |

## Confusion matrix: hybrid (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 30 | 0 | 4 |
| not_opt_out | 0 | 20 | 0 |
| ambiguous | 0 | 0 | 9 |

## Route() outcomes (auto=0.9, confirm=0.6)

| method | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| keyword | 15 | 0 | 0 | 48 |
| hybrid | 26 | 4 | 13 | 20 |

Hybrid route by true label:

| true | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| opt_out | 26 | 4 | 4 | 0 |
| not_opt_out | 0 | 0 | 0 | 20 |
| ambiguous | 0 | 0 | 9 | 0 |

## Threshold sweep (hybrid)

auto_opt_out when label=opt_out and confidence >= threshold. Recall = share of true opt-outs auto-handled. False opt-out rate = share of true non-opt-outs (not_opt_out + ambiguous) auto-opted-out.

| auto_threshold | recall | false_opt_out_rate |
|---|---|---|
| 0.50 | 0.882 | 0.000 |
| 0.60 | 0.882 | 0.000 |
| 0.70 | 0.882 | 0.000 |
| 0.80 | 0.853 | 0.000 |
| 0.85 | 0.853 | 0.000 |
| 0.90 | 0.765 | 0.000 |
| 0.95 | 0.441 | 0.000 |
| 0.99 | 0.000 | 0.000 |

## Token usage

- New API calls this run: 63 (cache hits: 0)
- Tokens this run (input/output): 42147 / 2869
- Tokens of all cached responses used (input/output): 42147 / 2869

## Cost and latency (LLM calls only)

Prices (USD per million tokens, input/output): {'input': 0.1, 'output': 0.5}. Latency is wall-clock time of one API call, measured only on calls made after latency logging was added (n=63 of 63 LLM-routed rows).

- Cost per LLM-routed message: $0.000090 (about $8.97 per 100,000 messages)
- Cost of all rows in this run: $0.0056
- Latency p50 / p95 / max: 883 / 2163 / 3406 ms
