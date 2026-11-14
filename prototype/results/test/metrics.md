# Opt-out classifier evaluation

Provider: `anthropic`, model: `claude-haiku-5-5`, rows evaluated: 175, LLM parse failures: 0

Binary metrics: opt_out is positive; ambiguous and not_opt_out both count as negative.

## Overall (opt_out)

| method | precision | recall | F1 | headline recall (soft_refusal) | FPR on keyword_trap |
|---|---|---|---|---|---|
| keyword | 0.550 | 0.306 | 0.393 | 0.000 (n=50) | 1.000 (n=18) |
| hybrid | 1.000 | 0.889 | 0.941 | 0.840 (n=50) | 0.000 (n=18) |

## Recall by opt_out category

| category | keyword | hybrid |
|---|---|---|
| keyword | 1.000 | 1.000 |
| soft_refusal | 0.000 | 0.840 |

## By language

| method | lang | n | precision | recall | F1 |
|---|---|---|---|---|---|
| keyword | en | 151 | 0.550 | 0.349 | 0.427 |
| keyword | es | 10 | 0.000 | 0.000 | 0.000 |
| keyword | ru | 14 | 0.000 | 0.000 | 0.000 |
| hybrid | en | 151 | 1.000 | 0.873 | 0.932 |
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
| opt_out | 64 | 0 | 8 |
| not_opt_out | 0 | 78 | 12 |
| ambiguous | 0 | 2 | 11 |

## Route() outcomes (auto=0.9, confirm=0.6)

| method | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| keyword | 40 | 0 | 0 | 135 |
| hybrid | 55 | 9 | 31 | 80 |

Hybrid route by true label:

| true | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| opt_out | 55 | 9 | 8 | 0 |
| not_opt_out | 0 | 0 | 12 | 78 |
| ambiguous | 0 | 0 | 11 | 2 |

## Threshold sweep (hybrid)

auto_opt_out when label=opt_out and confidence >= threshold. Recall = share of true opt-outs auto-handled. False opt-out rate = share of true non-opt-outs (not_opt_out + ambiguous) auto-opted-out.

| auto_threshold | recall | false_opt_out_rate |
|---|---|---|
| 0.50 | 0.889 | 0.000 |
| 0.60 | 0.889 | 0.000 |
| 0.70 | 0.889 | 0.000 |
| 0.80 | 0.847 | 0.000 |
| 0.85 | 0.806 | 0.000 |
| 0.90 | 0.764 | 0.000 |
| 0.95 | 0.681 | 0.000 |
| 0.99 | 0.306 | 0.000 |

## Token usage

- New API calls this run: 0 (cache hits: 153)
- Tokens this run (input/output): 0 / 0
- Tokens of all cached responses used (input/output): 56762 / 8507
