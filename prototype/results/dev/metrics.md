# Opt-out classifier evaluation

Provider: `anthropic`, model: `claude-haiku-5-5`, rows evaluated: 275, LLM parse failures: 0

Binary metrics: opt_out is positive; ambiguous and not_opt_out both count as negative.

## Overall (opt_out)

| method | precision | recall | F1 | headline recall (soft_refusal) | FPR on keyword_trap |
|---|---|---|---|---|---|
| keyword | 0.571 | 0.293 | 0.387 | 0.000 (n=85) | 1.000 (n=27) |
| hybrid | 0.991 | 0.943 | 0.967 | 0.918 (n=85) | 0.037 (n=27) |

## Recall by opt_out category

| category | keyword | hybrid |
|---|---|---|
| keyword | 0.947 | 1.000 |
| soft_refusal | 0.000 | 0.918 |

## Label accuracy by category (predicted label equals true label)

| category | n | keyword | hybrid |
|---|---|---|---|
| ambiguous | 11 | 0/11 | 8/11 |
| deferral | 13 | 13/13 | 4/13 |
| frustrated | 18 | 0/18 | 17/18 |
| keyword | 38 | 36/38 | 38/38 |
| keyword_trap | 27 | 0/27 | 26/27 |
| positive | 34 | 34/34 | 33/34 |
| question | 37 | 37/37 | 37/37 |
| soft_refusal | 85 | 0/85 | 78/85 |
| wrong_number_or_other | 12 | 12/12 | 9/12 |

## By language

| method | lang | n | precision | recall | F1 |
|---|---|---|---|---|---|
| keyword | en | 239 | 0.542 | 0.296 | 0.383 |
| keyword | es | 20 | 1.000 | 0.250 | 0.400 |
| keyword | ru | 16 | 1.000 | 0.286 | 0.444 |
| hybrid | en | 239 | 0.990 | 0.935 | 0.962 |
| hybrid | es | 20 | 1.000 | 1.000 | 1.000 |
| hybrid | ru | 16 | 1.000 | 1.000 | 1.000 |

## Confusion matrix: keyword (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 36 | 87 | 0 |
| not_opt_out | 27 | 96 | 0 |
| ambiguous | 0 | 29 | 0 |

## Confusion matrix: hybrid (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 116 | 0 | 7 |
| not_opt_out | 1 | 109 | 13 |
| ambiguous | 0 | 4 | 25 |

## Route() outcomes (auto=0.9, confirm=0.6)

| method | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| keyword | 63 | 0 | 0 | 212 |
| hybrid | 94 | 23 | 45 | 113 |

Hybrid route by true label:

| true | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| opt_out | 94 | 22 | 7 | 0 |
| not_opt_out | 0 | 1 | 13 | 109 |
| ambiguous | 0 | 0 | 25 | 4 |

## Threshold sweep (hybrid)

auto_opt_out when label=opt_out and confidence >= threshold. Recall = share of true opt-outs auto-handled. False opt-out rate = share of true non-opt-outs (not_opt_out + ambiguous) auto-opted-out.

| auto_threshold | recall | false_opt_out_rate |
|---|---|---|
| 0.50 | 0.943 | 0.007 |
| 0.60 | 0.943 | 0.007 |
| 0.70 | 0.943 | 0.007 |
| 0.80 | 0.862 | 0.000 |
| 0.85 | 0.789 | 0.000 |
| 0.90 | 0.764 | 0.000 |
| 0.95 | 0.626 | 0.000 |
| 0.99 | 0.293 | 0.000 |

## Token usage

- New API calls this run: 0 (cache hits: 239)
- Tokens this run (input/output): 0 / 0
- Tokens of all cached responses used (input/output): 88845 / 15070

## Cost and latency (LLM calls only)

Prices (USD per million tokens, input/output): {'input': 0.1, 'output': 0.5}. Latency is wall-clock time of one API call, measured only on calls made after latency logging was added (n=0 of 239 LLM-routed rows).

- Cost per LLM-routed message: $0.000069 (about $6.87 per 100,000 messages)
- Cost of all rows in this run: $0.0164
