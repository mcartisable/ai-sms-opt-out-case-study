# Opt-out classifier evaluation

Provider: `anthropic`, model: `claude-haiku-5-5`, rows evaluated: 450, LLM parse failures: 0

Binary metrics: opt_out is positive; ambiguous and not_opt_out both count as negative.

## Overall (opt_out)

| method | precision | recall | F1 | headline recall (soft_refusal) | FPR on keyword_trap |
|---|---|---|---|---|---|
| keyword | 0.563 | 0.297 | 0.389 | 0.000 (n=135) | 1.000 (n=45) |
| hybrid | 0.994 | 0.923 | 0.957 | 0.889 (n=135) | 0.022 (n=45) |

## Recall by opt_out category

| category | keyword | hybrid |
|---|---|---|
| keyword | 0.967 | 1.000 |
| soft_refusal | 0.000 | 0.889 |

## By language

| method | lang | n | precision | recall | F1 |
|---|---|---|---|---|---|
| keyword | en | 390 | 0.545 | 0.316 | 0.400 |
| keyword | es | 30 | 1.000 | 0.167 | 0.286 |
| keyword | ru | 30 | 1.000 | 0.167 | 0.286 |
| hybrid | en | 390 | 0.994 | 0.912 | 0.951 |
| hybrid | es | 30 | 1.000 | 1.000 | 1.000 |
| hybrid | ru | 30 | 1.000 | 1.000 | 1.000 |

## Confusion matrix: keyword (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 58 | 137 | 0 |
| not_opt_out | 45 | 168 | 0 |
| ambiguous | 0 | 42 | 0 |

## Confusion matrix: hybrid (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 180 | 0 | 15 |
| not_opt_out | 1 | 187 | 25 |
| ambiguous | 0 | 6 | 36 |

## Route() outcomes (auto=0.9, confirm=0.6)

| method | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| keyword | 103 | 0 | 0 | 347 |
| hybrid | 149 | 32 | 76 | 193 |

Hybrid route by true label:

| true | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| opt_out | 149 | 31 | 15 | 0 |
| not_opt_out | 0 | 1 | 25 | 187 |
| ambiguous | 0 | 0 | 36 | 6 |

## Threshold sweep (hybrid)

auto_opt_out when label=opt_out and confidence >= threshold. Recall = share of true opt-outs auto-handled. False opt-out rate = share of true non-opt-outs (not_opt_out + ambiguous) auto-opted-out.

| auto_threshold | recall | false_opt_out_rate |
|---|---|---|
| 0.50 | 0.923 | 0.004 |
| 0.60 | 0.923 | 0.004 |
| 0.70 | 0.923 | 0.004 |
| 0.80 | 0.856 | 0.000 |
| 0.85 | 0.795 | 0.000 |
| 0.90 | 0.764 | 0.000 |
| 0.95 | 0.646 | 0.000 |
| 0.99 | 0.297 | 0.000 |

## Token usage

- New API calls this run: 0 (cache hits: 392)
- Tokens this run (input/output): 0 / 0
- Tokens of all cached responses used (input/output): 145607 / 23577
