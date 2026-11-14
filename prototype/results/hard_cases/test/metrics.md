# Opt-out classifier evaluation

Provider: `anthropic`, model: `claude-haiku-5-5`, rows evaluated: 41, LLM parse failures: 0

Binary metrics: opt_out is positive; ambiguous and not_opt_out both count as negative.

## Overall (opt_out)

| method | precision | recall | F1 | headline recall (soft_refusal) | FPR on keyword_trap |
|---|---|---|---|---|---|
| keyword | 0.455 | 0.312 | 0.370 | n/a (n=0) | n/a (n=0) |
| hybrid | 0.941 | 1.000 | 0.970 | n/a (n=0) | n/a (n=0) |

## Recall by opt_out category

| category | keyword | hybrid |
|---|---|---|
| buried_request | 0.750 | 0.250 |
| channel_switch | 0.000 | 1.000 |
| formatting | 0.333 | 1.000 |
| prompt_injection | 0.250 | 0.500 |
| sarcasm | 0.000 | 0.250 |
| third_party | 0.500 | 0.500 |
| threat | 0.333 | 0.333 |
| typo_keyword | 0.000 | 1.000 |

## Label accuracy by category (predicted label equals true label)

| category | n | keyword | hybrid |
|---|---|---|---|
| buried_request | 4 | 2/4 | 4/4 |
| channel_switch | 2 | 0/2 | 2/2 |
| command | 3 | 3/3 | 3/3 |
| confusable | 5 | 2/5 | 3/5 |
| formatting | 3 | 1/3 | 3/3 |
| negation | 3 | 2/3 | 3/3 |
| partial_scope | 3 | 0/3 | 1/3 |
| prompt_injection | 4 | 3/4 | 4/4 |
| sarcasm | 4 | 1/4 | 4/4 |
| third_party | 2 | 1/2 | 1/2 |
| threat | 3 | 1/3 | 3/3 |
| typo_keyword | 5 | 0/5 | 5/5 |

## By language

| method | lang | n | precision | recall | F1 |
|---|---|---|---|---|---|
| keyword | en | 41 | 0.455 | 0.312 | 0.370 |
| hybrid | en | 41 | 0.941 | 1.000 | 0.970 |

## Confusion matrix: keyword (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 5 | 11 | 0 |
| not_opt_out | 5 | 11 | 0 |
| ambiguous | 1 | 8 | 0 |

## Confusion matrix: hybrid (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 16 | 0 | 0 |
| not_opt_out | 0 | 15 | 1 |
| ambiguous | 1 | 3 | 5 |

## Route() outcomes (auto=0.9, confirm=0.6)

| method | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| keyword | 11 | 0 | 0 | 30 |
| hybrid | 17 | 0 | 6 | 18 |

Hybrid route by true label:

| true | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| opt_out | 16 | 0 | 0 | 0 |
| not_opt_out | 0 | 0 | 1 | 15 |
| ambiguous | 1 | 0 | 5 | 3 |

## Threshold sweep (hybrid)

auto_opt_out when label=opt_out and confidence >= threshold. Recall = share of true opt-outs auto-handled. False opt-out rate = share of true non-opt-outs (not_opt_out + ambiguous) auto-opted-out.

| auto_threshold | recall | false_opt_out_rate |
|---|---|---|
| 0.50 | 1.000 | 0.040 |
| 0.60 | 1.000 | 0.040 |
| 0.70 | 1.000 | 0.040 |
| 0.80 | 1.000 | 0.040 |
| 0.85 | 1.000 | 0.040 |
| 0.90 | 1.000 | 0.040 |
| 0.95 | 0.812 | 0.040 |
| 0.99 | 0.062 | 0.040 |

## Token usage

- New API calls this run: 0 (cache hits: 39)
- Tokens this run (input/output): 0 / 0
- Tokens of all cached responses used (input/output): 14495 / 2015

## Cost and latency (LLM calls only)

Prices (USD per million tokens, input/output): {'input': 0.1, 'output': 0.5}. Latency is wall-clock time of one API call, measured only on calls made after latency logging was added (n=39 of 39 LLM-routed rows).

- Cost per LLM-routed message: $0.000063 (about $6.30 per 100,000 messages)
- Cost of all rows in this run: $0.0025
- Latency p50 / p95 / max: 899 / 2092 / 3090 ms
