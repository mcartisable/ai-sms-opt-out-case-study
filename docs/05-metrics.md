# Metrics

Case study based on my work as a PM at Maestra.io. No real Maestra figures appear here. All targets are illustrative assumptions and would be reset after the baseline is measured.

## North star

**Share of opt-out intent captured:** the share of subscribers who expressed an opt-out intent in a reply and were removed (or confirmed and removed) within 24 hours, counting keyword and non-keyword replies together. This matches the primary metric in `03-prd.md`, which focuses on non-keyword requests. I report both numbers.

Baseline for non-keyword requests is close to 0% because only keywords work. Target at full rollout: 85% (illustrative assumption).

## Input metrics

| Metric | Why | Target (illustrative) |
|---|---|---|
| Recall on non-keyword opt-outs | Direct driver of the north star | 90% offline |
| Share of opt-outs handled automatically | Reduces review workload | 70% |
| Confirmation reply rate | Shows if the step works | 40% |
| Review queue time to decision | Review is the slow path | Median under 24 hours |
| Brands with the flag on | Adoption | 60% of eligible brands after a year |

## Guardrails

| Guardrail | Definition | Threshold (illustrative) |
|---|---|---|
| False opt-out rate | Willing subscribers removed by the classifier, over all classifier-opt-outs | Under 2% |
| Complaint rate | Spam reports and complaints per 1,000 messages, per brand | No increase over the pre-launch baseline |
| Carrier filtering rate | Share of messages filtered or blocked | No increase over baseline |
| Reversal rate | Restores by a brand admin, over classifier opt-outs | Under 3% |
| Latency | Time from reply received to decision | p95 under 5 seconds for the classifier call |
| Cost per message | Model cost per classified reply | Under $0.002 |

A breach of the first four stops phase advancement and can trigger the kill switch described in `06-rollout-plan.md`.

## Offline evaluation

Run before any live traffic, on a hand-labeled set with the taxonomy from `02-discovery.md`. The synthetic `data/replies.csv` serves for prototyping only. A real evaluation needs real replies labeled by two people.

- **Recall on non-keyword opt-outs** (the soft refusal class; frustrated replies without an explicit request are labeled ambiguous). This is the headline offline number.
- **False opt-out rate** on not-opt-out, keyword-trap and ambiguous classes.
- **Per-language results.** A language without enough labeled examples (illustrative assumption: fewer than 200) cannot be set to auto opt-out.
- **Confusion by class**, and calibration of confidence against actual accuracy, because thresholds depend on it.
- **Injection set.** Replies that try to instruct the model, with the expectation of `unclear` or normal classification.

Offline gate: recall at or above 90% and false opt-out rate at or below 2% at the chosen auto threshold, in each language where auto opt-out is enabled.

## Online evaluation

**Shadow mode.** The classifier runs on live replies and takes no action. Compare its labels with what a reviewer decides on a sample. This measures real-world recall and false opt-out rate with no customer impact.

**A/B design.** After shadow, randomize at the subscriber level within a brand, or at the brand level for brands that prefer it. Control gets keyword-only handling. Treatment gets the full flow. Compare complaint rate, carrier filtering, opt-out capture and revenue per subscriber. Complaint rates move slowly and have low base rates, so the test needs several weeks and enough volume. Sample size depends on the brand's baseline, and I would compute it per brand before starting.

## Decision criteria to advance

| From | To | Criteria |
|---|---|---|
| Shadow | Human review queue | Offline gate met, shadow recall at or above 85% on sampled replies, no outage in 2 weeks |
| Review queue | Confirmation SMS | Reviewer agreement with classifier above 90%, legal approves confirmation wording, queue median under 24 hours |
| Confirmation SMS | Auto opt-out | Confirmation false positives under 2%, reversal rate under 3%, complaint and filtering rates not above baseline, per language |
