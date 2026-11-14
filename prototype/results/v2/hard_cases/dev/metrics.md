# Opt-out classifier evaluation

Provider: `anthropic`, model: `claude-haiku-5-5`, rows evaluated: 63, LLM parse failures: 0

Binary metrics: opt_out is positive; ambiguous and not_opt_out both count as negative.

## Overall (opt_out)

| method | precision | recall | F1 | headline recall (soft_refusal) | FPR on keyword_trap |
|---|---|---|---|---|---|
| keyword | 0.250 | 0.107 | 0.150 | n/a (n=0) | n/a (n=0) |
| hybrid | 0.926 | 0.893 | 0.909 | n/a (n=0) | n/a (n=0) |

## Recall by opt_out category

| category | keyword | hybrid |
|---|---|---|
| buried_request | 0.333 | 0.833 |
| channel_switch | 0.000 | 0.000 |
| formatting | 0.000 | 1.000 |
| prompt_injection | 0.167 | 0.167 |
| sarcasm | 0.000 | 0.333 |
| third_party | 0.250 | 0.500 |
| threat | 0.000 | 0.800 |
| typo_keyword | 0.000 | 1.000 |

## Label accuracy by category (predicted label equals true label)

| category | n | keyword | hybrid |
|---|---|---|---|
| buried_request | 6 | 1/6 | 6/6 |
| channel_switch | 2 | 0/2 | 0/2 |
| command | 5 | 5/5 | 4/5 |
| confusable | 7 | 2/7 | 4/7 |
| formatting | 5 | 0/5 | 5/5 |
| negation | 5 | 2/5 | 5/5 |
| partial_scope | 5 | 0/5 | 5/5 |
| prompt_injection | 6 | 6/6 | 4/6 |
| sarcasm | 6 | 1/6 | 6/6 |
| third_party | 4 | 1/4 | 3/4 |
| threat | 5 | 0/5 | 4/5 |
| typo_keyword | 7 | 0/7 | 7/7 |

## By language

| method | lang | n | precision | recall | F1 |
|---|---|---|---|---|---|
| keyword | en | 63 | 0.250 | 0.107 | 0.150 |
| hybrid | en | 63 | 0.926 | 0.893 | 0.909 |

## Confusion matrix: keyword (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 3 | 25 | 0 |
| not_opt_out | 7 | 15 | 0 |
| ambiguous | 2 | 11 | 0 |

## Confusion matrix: hybrid (rows = true, cols = predicted)

| true \ pred | opt_out | not_opt_out | ambiguous |
|---|---|---|---|
| opt_out | 25 | 0 | 3 |
| not_opt_out | 0 | 17 | 5 |
| ambiguous | 2 | 0 | 11 |

## Route() outcomes (auto=0.9, confirm=0.6)

| method | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| keyword | 12 | 0 | 0 | 51 |
| hybrid | 21 | 6 | 19 | 17 |

Hybrid route by true label:

| true | auto_opt_out | send_confirmation | human_review | no_action |
|---|---|---|---|---|
| opt_out | 20 | 5 | 3 | 0 |
| not_opt_out | 0 | 0 | 5 | 17 |
| ambiguous | 1 | 1 | 11 | 0 |

## Threshold sweep (hybrid)

auto_opt_out when label=opt_out and confidence >= threshold. Recall = share of true opt-outs auto-handled. False opt-out rate = share of true non-opt-outs (not_opt_out + ambiguous) auto-opted-out.

| auto_threshold | recall | false_opt_out_rate |
|---|---|---|
| 0.50 | 0.893 | 0.057 |
| 0.60 | 0.893 | 0.057 |
| 0.70 | 0.893 | 0.029 |
| 0.80 | 0.893 | 0.029 |
| 0.85 | 0.786 | 0.029 |
| 0.90 | 0.714 | 0.029 |
| 0.95 | 0.464 | 0.029 |
| 0.99 | 0.071 | 0.000 |

## Token usage

- New API calls this run: 63 (cache hits: 0)
- Tokens this run (input/output): 36093 / 6101
- Tokens of all cached responses used (input/output): 36093 / 6101

## Cost and latency (LLM calls only)

Prices (USD per million tokens, input/output): {'input': 0.1, 'output': 0.5}. Latency is wall-clock time of one API call, measured only on calls made after latency logging was added (n=63 of 63 LLM-routed rows).

- Cost per LLM-routed message: $0.000106 (about $10.57 per 100,000 messages)
- Cost of all rows in this run: $0.0067
- Latency p50 / p95 / max: 1423 / 3233 / 4347 ms
