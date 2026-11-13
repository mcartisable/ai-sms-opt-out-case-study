# AI SMS Opt-Out: detecting natural-language unsubscribe requests

SMS marketing platforms like Maestra.io only honored keywords such as STOP, so replies like "I don't want to receive messages from you anymore" stayed subscribed. This project is a PM case study plus a working prototype that uses an LLM to catch those unsubscribe requests.

It is based on my product work at Maestra.io. All data here is synthetic and all business figures are illustrative assumptions. No confidential data is included.

## Problem

Maestra's SMS opt-out only worked on keywords. Customers often wrote refusals in their own words, with no keyword, and kept receiving messages. That is a compliance risk for the brand, a bad experience for the customer, and a source of complaints and carrier filtering for the platform. Details and the illustrative sizing are in [docs/01-problem-and-context.md](docs/01-problem-and-context.md).

## Approach

Keyword rules still run first because they are fast and deterministic. Replies without a keyword go to a small, cheap LLM (`claude-haiku-5-5`) that returns a label (`opt_out`, `not_opt_out`, `ambiguous`) and a confidence. Confidence thresholds route each reply:

| Condition | Action |
|---|---|
| opt_out, confidence >= 0.90 | opt the customer out automatically |
| opt_out, confidence 0.60 to 0.90 | send a confirmation SMS ("Reply YES to unsubscribe") |
| ambiguous, or low confidence | human review queue |
| not_opt_out | no action |

The false-negative cost (a customer who wanted out stays subscribed) is much higher than the false-positive cost (a willing subscriber is removed), so the auto threshold is set high and uncertain cases go to confirmation or review. The reasoning is in [docs/04-risk-and-compliance.md](docs/04-risk-and-compliance.md), the requirements in [docs/03-prd.md](docs/03-prd.md).

## Results

Offline evaluation on 450 synthetic replies (English, Russian, Spanish), including keyword traps like "cancel my order" and "don't stop the sales". Model: `claude-haiku-5-5`, 0 parse failures. Full output in [prototype/results/metrics.md](prototype/results/metrics.md).

| Method | Recall on opt-outs with no keyword (n=130) | False opt-out on keyword traps (n=45) | Overall opt-out precision / recall |
|---|---|---|---|
| Keyword rules (baseline) | 0% | 100% | 0.56 / 0.31 |
| Keyword + LLM (hybrid) | 92% | 2% | 0.99 / 0.95 |

What the routing did with the hybrid's decisions:
- All 190 true opt-outs ended up auto-opted-out (149), sent a confirmation (31), or sent to human review (10). None were ignored.
- At the 0.90 auto threshold, 0 non-opt-outs and 0 ambiguous replies were opted out automatically. The single false positive ("Quit it with the flash sales lol") scored 0.75, so it only triggered a confirmation SMS.
- The 10 missed soft refusals were borderline phrasings ("I'm done with these texts", "get lost already with your promos") scored ambiguous at 0.6 to 0.7.
- Raising the auto threshold trades recall for safety: auto-handled opt-outs fall from 78% at 0.90 to 66% at 0.95, with the rest going to confirmation or review.
- Cost: about 146k input and 24k output tokens for all 450 messages.

Caveats. The dataset is generated from templates with typos and prefixes, so many rows are close variants of each other, and real inbound SMS is messier. Treat these numbers as an upper bound that shows the approach works, and as the harness for measuring real data in a shadow-mode rollout ([docs/06-rollout-plan.md](docs/06-rollout-plan.md)). The keyword baseline's 0% is true by construction, because the soft-refusal rows contain no keyword.

## Repo structure

```
docs/        PM case study: problem, discovery, PRD, risk, metrics, rollout, decision log
data/        generate_dataset.py and the synthetic replies.csv (450 rows)
prototype/   classifier.py (keyword, LLM, hybrid, routing), evaluate.py, results/
```

## How to run

```bash
pip3 install -r requirements.txt
python3 prototype/evaluate.py --provider mock --sample-per-category 10   # offline pipeline test, not real results
export ANTHROPIC_API_KEY=your-key
python3 prototype/evaluate.py --provider anthropic                       # real run, 450 rows
```

Responses are cached in `prototype/results/`, so reruns are free. Delete the cache after editing the system prompt.

## What I learned

- **Test the harness before trusting the model.** My first real run scored 35% recall because I capped the model's output length too low and a quarter of the answers were cut off. The number looked like a model weakness and was a bug.
- **Check the labels.** I first labeled angry replies like "Who the heck keeps texting me?" as opt-outs. The model called them ambiguous, and on reflection it was right. Relabeling them changed the headline metric more than any model change would have.
- **The routing matters more than the classifier.** The model's borderline calls are mostly handled by confirmation and review tiers, which is what keeps false opt-outs at zero at the auto threshold.
