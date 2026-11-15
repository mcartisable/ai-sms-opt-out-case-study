# AI SMS Opt-Out: detecting natural-language unsubscribe requests

By Ruslan Temirgaliev, product manager. Based on my work on SMS opt-out at Maestra.io.

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

Offline evaluation on 450 synthetic replies (English, Russian, Spanish), including keyword traps like "cancel my order" and "don't stop the sales". Model: `claude-haiku-5-5`, 0 parse failures. Labels follow [data/LABELING_POLICY.md](data/LABELING_POLICY.md), which was revised after a blind hand-labeling check of 70 messages. Full output in [prototype/results/metrics.md](prototype/results/metrics.md).

| Method | Recall on opt-outs with no keyword (n=135) | False opt-out on keyword traps (n=45) | Overall opt-out precision / recall |
|---|---|---|---|
| Keyword rules (baseline) | 0% | 100% | 0.56 / 0.30 |
| Keyword + LLM (hybrid) | 89% | 2% | 0.99 / 0.92 |

The data is split by phrase family into a dev set (275 rows) and a held-out test set (175 rows). Recall on opt-outs with no keyword is 92% on dev (78 of 85) and 84% on test (42 of 50, 95% interval 71% to 92%). The test number is the one to quote. Output for each split is in `prototype/results/dev` and `prototype/results/test`.

What the routing did with the hybrid's decisions:
- All 195 true opt-outs ended up auto-opted-out (149), sent a confirmation (31), or sent to human review (15). None were ignored.
- At the 0.90 auto threshold, 0 non-opt-outs and 0 ambiguous replies were opted out automatically. The single false positive ("Quit it with the flash sales lol") scored 0.75, so it only triggered a confirmation SMS.
- The 15 opt-outs sent to review include 10 borderline refusals ("I'm done with these texts", "get lost already with your promos") and all 5 "I never signed up for this garbage" replies, which the model scores as ambiguous at 0.6. That is the first target for prompt version 2.
- Raising the auto threshold trades recall for safety: auto-handled opt-outs fall from 76% at 0.90 to 65% at 0.95, with the rest going to confirmation or review.
- A cost to watch: 25 of the 213 true non-opt-outs, mostly deferrals like "Not now", go to human review, because the model calls them ambiguous and the labeling policy says they need no action. That is wasted review work.
- Token cost: about 146k input and 24k output tokens for all 450 messages.

Prompt v3 (details in [docs/09-prompt-iterations.md](docs/09-prompt-iterations.md)). After reading v1's misses ([docs/08-error-analysis.md](docs/08-error-analysis.md)) I rewrote the prompt three times against the dev split only, then scored the held-out test split once. Recall on opt-outs with no keyword went from 84% to 100% on test (50 of 50, interval 93% to 100%), real opt-outs sent to human review dropped from 8 to 0 of 72, and harmless messages sent to review dropped from 12 to 3 of 90. No non-opt-out was opted out or sent a confirmation. I also fixed a bug found along the way: any message of three words or fewer containing a keyword skipped the model, so "Cancel my subscription" was opted out. Cost is about $0.00009 per classified message and latency p50 is about 1 second. Read the 100% as a ceiling: I looked at test misses while analyzing v1, the data is template-generated, and the hard-set labels are mine alone. On a fresh batch of 63 messages written before any run ([docs/11-fresh-batch.md](docs/11-fresh-batch.md)), v3 labeled 91% of the 33 opt-outs correctly (interval 76% to 97%), sent 26 to automatic opt-out, 4 to confirmation and 3 to human review, ignored none, and opted out no harmless message. That is the number to quote.

Caveats. The dataset is generated from templates with typos and prefixes, so many rows are close variants of each other, and real inbound SMS is messier. Treat these numbers as an upper bound that shows the approach works, and as the harness for measuring real data in a shadow-mode rollout ([docs/06-rollout-plan.md](docs/06-rollout-plan.md)). The keyword baseline's 0% is true by construction, because the soft-refusal rows contain no keyword. The labels came from the same generator as the messages. A blind human pass on 70 messages agreed on 84% (Cohen's kappa 0.76), and all disagreements were in the generator's `ambiguous` bucket.

## Repo structure

```
docs/        PM case study: problem, discovery, PRD, risk, metrics, rollout, decision log
data/        generate_dataset.py and the synthetic replies.csv (450 rows)
prototype/   classifier.py (keyword, LLM, hybrid, routing), evaluate.py, results/
demo/        Cloudflare Pages demo: recorded answers plus a rate-limited live box
integration/ handoff kit for engineering: classifier package, rollout-mode handler, shadow-mode log and report, INTEGRATION.md
```

## How to run

```bash
pip3 install -r requirements.txt
python3 prototype/evaluate.py --provider mock --sample-per-category 10   # offline pipeline test, not real results
export ANTHROPIC_API_KEY=your-key
python3 prototype/evaluate.py --provider anthropic                       # real run, 450 rows, prompt v3
prototype/run_split.sh v3 test                                           # one split of both datasets, one prompt version
```

Responses are cached in `prototype/results/`, so reruns are free. Delete the cache after editing the system prompt.

## What I learned

- **Test the harness before trusting the model.** My first real run scored 35% recall because I capped the model's output length too low and a quarter of the answers were cut off. The number looked like a model weakness and was a bug.
- **Check the labels.** I first labeled angry replies like "Who the heck keeps texting me?" as opt-outs. The model called them ambiguous, and on reflection it was right. Relabeling them changed the headline metric more than any model change would have.
- **Labels are policy.** I labeled 70 messages blind and compared them with the generator's labels. They matched on every clear opt-out and non-opt-out, and disagreed on "Not now", "Maybe later", "Who is this?" and "I never signed up". Adopting my labels moved the headline recall from 92% to 89% without touching the model, and exposed a real gap in the prompt.
- **The routing matters more than the classifier.** The model's borderline calls are mostly handled by confirmation and review tiers, which is what keeps false opt-outs at zero at the auto threshold.

## License

MIT, see [LICENSE](LICENSE). The code and docs may be copied and adapted. The case study figures are illustrative, the data is synthetic, and nothing here is legal advice. Check opt-out rules for your own markets with a compliance reviewer before using any of it in production.

