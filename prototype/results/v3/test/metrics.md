# Opt-out classifier evaluation

Provider: `anthropic`, model: `claude-haiku-5-5`, rows evaluated: 175, LLM parse failures: 0

Binary metrics: opt_out is positive; ambiguous and not_opt_out both count as negative.

## Overall (opt_out)

| method | precision | recall | F1 | headline recall (soft_refusal) | FPR on keyword_trap |
|---|---|---|---|---|---|
| keyword | 0.550 | 0.306 | 0.393 | 0.000 (n=50) | 1.000 (n=18) |
| hybrid | 1.000 | 1.000 | 1.000 | 1.000 (n=50) | 0.000 (n=18) |

## Recall by opt_out category

| category | keyword | hybrid |
|---|---|---|
| keyword | 1.000 | 1.000 |
| soft_refusal | 0.000 | 1.000 |

## Label accuracy by category (predicted label equals true label)

| category | n | keyword | hybrid |
|---|---|---|---|
| ambiguous | 3 | 0/3 | 3/3 |
| deferral | 14 | 11/14 | 10/14 |
| frustrated | 7 | 0/7 | 7/7 |
| keyword | 22 | 22/22 | 22/22 |
| keyword_trap | 18 | 0/18 | 18/18 |
| positive | 21 | 21/21 | 21/21 |
| question | 27 | 27/27 | 27/27 |
| soft_refusal | 50 | 0/50 | 50/50 |
| wrong_number_or_other | 13 | 13/13 | 11/13 |

## By language

| method | lang | n | precision | recall | F1 |
|---|---|---|---|---|---|
| keyword | en | 151 | 0.550 | 0.349 | 0.427 |
| keyword | es | 10 | 0.000 | 0.000 | 0.000 |
| keyword | ru | 14 | 0.000 | 0.000 | 0.000 |
| hybrid | en | 151 | 1.000 | 1.000 | 1.000 |
| hybrid | es | 10 | 1.000 | 1.000 | 1.000 |
| hybrid | ru | 14 | 1.000 | 1.000 | 1.000 |

## Confusion matrix: keyword (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 22 | 50 | 0 |
| not_opt_out | 18 | 72 | 0 |
| ambiguous | 0 | 13 | 0 |

## Confusion matrix: hybrid (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 72 | 0 | 0 |
| not_opt_out | 0 | 87 | 3 |
| ambiguous | 0 | 3 | 10 |

## Route() outcomes (auto=0.9, confirm=0.6)

| method | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| keyword | 40 | 0 | 0 | 135 |
| hybrid | 66 | 6 | 13 | 90 |

Hybrid route by true label:

| true | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| opt_out | 66 | 6 | 0 | 0 |
| not_opt_out | 0 | 0 | 3 | 87 |
| ambiguous | 0 | 0 | 10 | 3 |

## Threshold sweep (hybrid)

auto_opt_out when label=opt_out and confidence >= threshold. Recall = share of true opt-outs auto-handled. False opt-out rate = share of true non-opt-outs (not_opt_out + ambiguous) auto-opted-out.

| auto_threshold | recall | false_opt_out_rate |
|---|---|---|
| 0.50 | 1.000 | 0.000 |
| 0.60 | 1.000 | 0.000 |
| 0.70 | 1.000 | 0.000 |
| 0.80 | 1.000 | 0.000 |
| 0.85 | 0.986 | 0.000 |
| 0.90 | 0.917 | 0.000 |
| 0.95 | 0.764 | 0.000 |
| 0.99 | 0.181 | 0.000 |

## Token usage

- New API calls this run: 162 (cache hits: 0)
- Tokens this run (input/output): 108156 / 6163
- Tokens of all cached responses used (input/output): 108156 / 6163

## Cost and latency (LLM calls only)

Prices (USD per million tokens, input/output): {'input': 0.1, 'output': 0.5}. Latency is wall-clock time of one API call, measured only on calls made after latency logging was added (n=162 of 162 LLM-routed rows).

- Cost per LLM-routed message: $0.000086 (about $8.58 per 100,000 messages)
- Cost of all rows in this run: $0.0139
- Latency p50 / p95 / max: 950 / 1993 / 2742 ms
