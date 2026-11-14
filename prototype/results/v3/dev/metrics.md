# Opt-out classifier evaluation

Provider: `anthropic`, model: `claude-haiku-5-5`, rows evaluated: 275, LLM parse failures: 0

Binary metrics: opt_out is positive; ambiguous and not_opt_out both count as negative.

## Overall (opt_out)

| method | precision | recall | F1 | headline recall (soft_refusal) | FPR on keyword_trap |
|---|---|---|---|---|---|
| keyword | 0.571 | 0.293 | 0.387 | 0.000 (n=85) | 1.000 (n=27) |
| hybrid | 0.946 | 1.000 | 0.972 | 1.000 (n=85) | 0.037 (n=27) |

## Recall by opt_out category

| category | keyword | hybrid |
|---|---|---|
| keyword | 0.947 | 1.000 |
| soft_refusal | 0.000 | 1.000 |

## Label accuracy by category (predicted label equals true label)

| category | n | keyword | hybrid |
|---|---|---|---|
| ambiguous | 11 | 0/11 | 10/11 |
| deferral | 13 | 13/13 | 13/13 |
| frustrated | 18 | 0/18 | 10/18 |
| keyword | 38 | 36/38 | 38/38 |
| keyword_trap | 27 | 0/27 | 26/27 |
| positive | 34 | 34/34 | 33/34 |
| question | 37 | 37/37 | 37/37 |
| soft_refusal | 85 | 0/85 | 85/85 |
| wrong_number_or_other | 12 | 12/12 | 8/12 |

## By language

| method | lang | n | precision | recall | F1 |
|---|---|---|---|---|---|
| keyword | en | 239 | 0.542 | 0.296 | 0.383 |
| keyword | es | 20 | 1.000 | 0.250 | 0.400 |
| keyword | ru | 16 | 1.000 | 0.286 | 0.444 |
| hybrid | en | 239 | 0.947 | 1.000 | 0.973 |
| hybrid | es | 20 | 1.000 | 1.000 | 1.000 |
| hybrid | ru | 16 | 0.875 | 1.000 | 0.933 |

## Confusion matrix: keyword (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 36 | 87 | 0 |
| not_opt_out | 27 | 96 | 0 |
| ambiguous | 0 | 29 | 0 |

## Confusion matrix: hybrid (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 123 | 0 | 0 |
| not_opt_out | 1 | 117 | 5 |
| ambiguous | 6 | 3 | 20 |

## Route() outcomes (auto=0.9, confirm=0.6)

| method | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| keyword | 63 | 0 | 0 | 212 |
| hybrid | 115 | 15 | 25 | 120 |

Hybrid route by true label:

| true | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| opt_out | 112 | 11 | 0 | 0 |
| not_opt_out | 0 | 1 | 5 | 117 |
| ambiguous | 3 | 3 | 20 | 3 |

## Threshold sweep (hybrid)

auto_opt_out when label=opt_out and confidence >= threshold. Recall = share of true opt-outs auto-handled. False opt-out rate = share of true non-opt-outs (not_opt_out + ambiguous) auto-opted-out.

| auto_threshold | recall | false_opt_out_rate |
|---|---|---|
| 0.50 | 1.000 | 0.046 |
| 0.60 | 1.000 | 0.046 |
| 0.70 | 1.000 | 0.046 |
| 0.80 | 0.976 | 0.033 |
| 0.85 | 0.959 | 0.026 |
| 0.90 | 0.911 | 0.020 |
| 0.95 | 0.675 | 0.000 |
| 0.99 | 0.236 | 0.000 |

## Token usage

- New API calls this run: 250 (cache hits: 0)
- Tokens this run (input/output): 167117 / 9998
- Tokens of all cached responses used (input/output): 167117 / 9998

## Cost and latency (LLM calls only)

Prices (USD per million tokens, input/output): {'input': 0.1, 'output': 0.5}. Latency is wall-clock time of one API call, measured only on calls made after latency logging was added (n=250 of 250 LLM-routed rows).

- Cost per LLM-routed message: $0.000087 (about $8.68 per 100,000 messages)
- Cost of all rows in this run: $0.0217
- Latency p50 / p95 / max: 1172 / 2507 / 4967 ms
