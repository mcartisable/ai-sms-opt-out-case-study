# Opt-out classifier evaluation

Provider: `anthropic`, model: `claude-haiku-5-5`, rows evaluated: 275, LLM parse failures: 0

Binary metrics: opt_out is positive; ambiguous and not_opt_out both count as negative.

## Overall (opt_out)

| method | precision | recall | F1 | headline recall (soft_refusal) | FPR on keyword_trap |
|---|---|---|---|---|---|
| keyword | 0.571 | 0.293 | 0.387 | 0.000 (n=85) | 1.000 (n=27) |
| hybrid | 0.937 | 0.967 | 0.952 | 0.976 (n=85) | 0.037 (n=27) |

## Recall by opt_out category

| category | keyword | hybrid |
|---|---|---|
| keyword | 0.947 | 0.947 |
| soft_refusal | 0.000 | 0.976 |

## Label accuracy by category (predicted label equals true label)

| category | n | keyword | hybrid |
|---|---|---|---|
| ambiguous | 11 | 0/11 | 11/11 |
| deferral | 13 | 13/13 | 13/13 |
| frustrated | 18 | 0/18 | 11/18 |
| keyword | 38 | 36/38 | 36/38 |
| keyword_trap | 27 | 0/27 | 26/27 |
| positive | 34 | 34/34 | 33/34 |
| question | 37 | 37/37 | 33/37 |
| soft_refusal | 85 | 0/85 | 83/85 |
| wrong_number_or_other | 12 | 12/12 | 8/12 |

## By language

| method | lang | n | precision | recall | F1 |
|---|---|---|---|---|---|
| keyword | en | 239 | 0.542 | 0.296 | 0.383 |
| keyword | es | 20 | 1.000 | 0.250 | 0.400 |
| keyword | ru | 16 | 1.000 | 0.286 | 0.444 |
| hybrid | en | 239 | 0.937 | 0.963 | 0.950 |
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
| opt_out | 119 | 0 | 4 |
| not_opt_out | 1 | 113 | 9 |
| ambiguous | 7 | 0 | 22 |

## Route() outcomes (auto=0.9, confirm=0.6)

| method | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| keyword | 63 | 0 | 0 | 212 |
| hybrid | 113 | 14 | 35 | 113 |

Hybrid route by true label:

| true | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| opt_out | 111 | 8 | 4 | 0 |
| not_opt_out | 0 | 1 | 9 | 113 |
| ambiguous | 2 | 5 | 22 | 0 |

## Threshold sweep (hybrid)

auto_opt_out when label=opt_out and confidence >= threshold. Recall = share of true opt-outs auto-handled. False opt-out rate = share of true non-opt-outs (not_opt_out + ambiguous) auto-opted-out.

| auto_threshold | recall | false_opt_out_rate |
|---|---|---|
| 0.50 | 0.967 | 0.053 |
| 0.60 | 0.967 | 0.053 |
| 0.70 | 0.967 | 0.053 |
| 0.80 | 0.951 | 0.053 |
| 0.85 | 0.951 | 0.033 |
| 0.90 | 0.902 | 0.013 |
| 0.95 | 0.683 | 0.000 |
| 0.99 | 0.236 | 0.000 |

## Token usage

- New API calls this run: 250 (cache hits: 0)
- Tokens this run (input/output): 143117 / 11609
- Tokens of all cached responses used (input/output): 143117 / 11609

## Cost and latency (LLM calls only)

Prices (USD per million tokens, input/output): {'input': 0.1, 'output': 0.5}. Latency is wall-clock time of one API call, measured only on calls made after latency logging was added (n=250 of 250 LLM-routed rows).

- Cost per LLM-routed message: $0.000080 (about $8.05 per 100,000 messages)
- Cost of all rows in this run: $0.0201
- Latency p50 / p95 / max: 1399 / 3731 / 18270 ms
