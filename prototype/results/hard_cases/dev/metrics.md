# Opt-out classifier evaluation

Provider: `anthropic`, model: `claude-haiku-5-5`, rows evaluated: 63, LLM parse failures: 0

Binary metrics: opt_out is positive; ambiguous and not_opt_out both count as negative.

## Overall (opt_out)

| method | precision | recall | F1 | headline recall (soft_refusal) | FPR on keyword_trap |
|---|---|---|---|---|---|
| keyword | 0.333 | 0.138 | 0.195 | n/a (n=0) | n/a (n=0) |
| hybrid | 1.000 | 0.931 | 0.964 | n/a (n=0) | n/a (n=0) |

## Recall by opt_out category

| category | keyword | hybrid |
|---|---|---|
| buried_request | 0.333 | 0.833 |
| channel_switch | 0.000 | 0.500 |
| confusable | 0.571 | 0.143 |
| formatting | 0.000 | 1.000 |
| prompt_injection | 0.167 | 0.167 |
| sarcasm | 0.000 | 0.167 |
| third_party | 0.250 | 0.750 |
| threat | 0.000 | 0.600 |
| typo_keyword | 0.000 | 1.000 |

## Label accuracy by category (predicted label equals true label)

| category | n | keyword | hybrid |
|---|---|---|---|
| buried_request | 6 | 1/6 | 6/6 |
| channel_switch | 2 | 0/2 | 1/2 |
| command | 5 | 5/5 | 5/5 |
| confusable | 7 | 3/7 | 7/7 |
| formatting | 5 | 0/5 | 5/5 |
| negation | 5 | 2/5 | 5/5 |
| partial_scope | 5 | 0/5 | 4/5 |
| prompt_injection | 6 | 6/6 | 6/6 |
| sarcasm | 6 | 1/6 | 5/6 |
| third_party | 4 | 1/4 | 3/4 |
| threat | 5 | 0/5 | 5/5 |
| typo_keyword | 7 | 0/7 | 7/7 |

## By language

| method | lang | n | precision | recall | F1 |
|---|---|---|---|---|---|
| keyword | en | 63 | 0.333 | 0.138 | 0.195 |
| hybrid | en | 63 | 1.000 | 0.931 | 0.964 |

## Confusion matrix: keyword (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 4 | 25 | 0 |
| not_opt_out | 7 | 15 | 0 |
| ambiguous | 1 | 11 | 0 |

## Confusion matrix: hybrid (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 27 | 0 | 2 |
| not_opt_out | 0 | 22 | 0 |
| ambiguous | 0 | 2 | 10 |

## Route() outcomes (auto=0.9, confirm=0.6)

| method | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| keyword | 12 | 0 | 0 | 51 |
| hybrid | 23 | 4 | 12 | 24 |

Hybrid route by true label:

| true | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| opt_out | 23 | 4 | 2 | 0 |
| not_opt_out | 0 | 0 | 0 | 22 |
| ambiguous | 0 | 0 | 10 | 2 |

## Threshold sweep (hybrid)

auto_opt_out when label=opt_out and confidence >= threshold. Recall = share of true opt-outs auto-handled. False opt-out rate = share of true non-opt-outs (not_opt_out + ambiguous) auto-opted-out.

| auto_threshold | recall | false_opt_out_rate |
|---|---|---|
| 0.50 | 0.931 | 0.000 |
| 0.60 | 0.931 | 0.000 |
| 0.70 | 0.931 | 0.000 |
| 0.80 | 0.897 | 0.000 |
| 0.85 | 0.862 | 0.000 |
| 0.90 | 0.793 | 0.000 |
| 0.95 | 0.517 | 0.000 |
| 0.99 | 0.000 | 0.000 |

## Token usage

- New API calls this run: 0 (cache hits: 63)
- Tokens this run (input/output): 0 / 0
- Tokens of all cached responses used (input/output): 23430 / 5652

## Cost and latency (LLM calls only)

Prices (USD per million tokens, input/output): {'input': 0.1, 'output': 0.5}. Latency is wall-clock time of one API call, measured only on calls made after latency logging was added (n=63 of 63 LLM-routed rows).

- Cost per LLM-routed message: $0.000082 (about $8.20 per 100,000 messages)
- Cost of all rows in this run: $0.0052
- Latency p50 / p95 / max: 1307 / 2373 / 2640 ms
