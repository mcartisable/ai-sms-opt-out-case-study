# Concepts glossary

A running explainer of the ideas behind this project, written as the work is built. Each entry says what the idea is, why a PM cares, where it shows up in this repo, and a one-line version for interviews. Numbers come from the real run of `claude-haiku-5-5` on the 450 synthetic replies in `data/replies.csv`.

## Step 1: measuring the right thing

### Precision and recall
- **What it is.** Precision answers "of the messages we opted out, how many really wanted out?" Recall answers "of the customers who wanted out, how many did we catch?"
- **Why a PM cares.** They fail in different ways. Low recall means people who asked to stop keep getting texts. Low precision means people who still wanted messages get removed. One accuracy number hides which one is happening.
- **In this repo.** The hybrid scored precision 0.99 and recall 0.95 on opt-outs. The keyword rules scored 0.56 and 0.31: they catch some opt-outs, and they also fire on traps like "cancel my order".
- **One-liner.** "Recall is how many real opt-outs we caught, precision is how many of our opt-outs were real, and the product decision is which one we protect."

### False positives, false negatives and unequal costs
- **What it is.** A false negative here is a missed opt-out. A false positive is an opt-out of someone who didn't ask.
- **Why a PM cares.** The model doesn't know the costs; you do, and the thresholds encode them. A missed opt-out risks complaints and compliance trouble. A wrong opt-out loses a subscriber and some revenue, and a confirmation text can often win them back.
- **In this repo.** `docs/04-risk-and-compliance.md` puts illustrative costs on both errors, and `route()` in `prototype/classifier.py` turns the asymmetry into thresholds (auto opt-out at 0.90, confirmation text from 0.60).
- **One-liner.** "I set the threshold from the cost of each error, not from whichever accuracy looked best."

### Baseline
- **What it is.** The simplest thing you would do without the new feature, measured on the same data.
- **Why a PM cares.** An AI result means nothing alone. 92% recall only matters next to the 0% the keyword rules get on the same messages.
- **In this repo.** `keyword_classify()` is the baseline, and every table puts it beside the hybrid. The baseline's 0% on soft refusals is true by construction, since those rows contain no keyword. The comparison shows how large the gap is, not that the model is clever.
- **One-liner.** "Compare to what the product does today, not to nothing."

### Success metrics and guardrails
- **What it is.** A success metric is what you want to move. A guardrail is something that must not get worse while you move it.
- **Why a PM cares.** Without guardrails, you can raise recall by opting everyone out.
- **In this repo.** Success: recall on opt-outs with no keyword. Guardrails: false opt-out rate and the keyword-trap rate. Defined in `docs/05-metrics.md`.
- **One-liner.** "Every metric I push has a guardrail that catches the cheap way to game it."

### Dev set and test set
- **What it is.** The dev set is where you look at mistakes and tune the prompt. The test set is held back and scored once, to see how the result holds on messages you haven't studied.
- **Why a PM cares.** If you tune and measure on the same messages, the score rewards fitting those messages. A number from untouched data is the one you can promise stakeholders.
- **In this repo.** `data/replies.csv` now has a `split` column (about 60% dev, 40% test). Run `python3 prototype/evaluate.py --split test` for the held-out numbers.
- **One-liner.** "I tune on dev and report once on test."

### Data leakage and splitting by template family
- **What it is.** Leakage is when information from the test set sneaks into development. A common form is near-duplicates: the same message in slightly different wording on both sides of the split.
- **Why a PM cares.** It makes results look better than they will be in production.
- **In this repo.** Each dataset row is a variation of a base phrase ("please remove me from your list" with different casing, a typo, a "pls"). A random split would put near-copies in both sets. So the `family` column groups variants, and a whole family goes to one split. Checked: no family appears in both.
- **One-liner.** "Split by phrase family, not by row, because the rows are near-duplicates."

### Confidence intervals on small samples
- **What it is.** A single percentage hides how much it could move with a different sample. A 95% interval is the range the true value plausibly falls in.
- **Why a PM cares.** It stops you over-reading small differences.
- **In this repo.** Soft-refusal recall is 92% on dev (78 of 85, interval 84% to 96%) and 93% on test (42 of 45, interval 82% to 98%). The test number looks higher, but the intervals overlap heavily, so the difference means nothing. A single bad message moves the test score by 2 points.
- **One-liner.** "On 45 examples a 1-point difference is noise, so I report counts and intervals."

## Concepts already touched earlier in this project

### Keyword rules vs LLM classification
Rules are fast, free and exact but only see exact words. A language model reads meaning, so it catches "take me off your list" and handles Russian and Spanish, but it costs money per message, can be wrong, and returns a confidence rather than a certainty. The hybrid keeps rules first and sends only the rest to the model.

### Thresholds and routing
The model returns a label and a confidence. `route()` maps them to actions. This is how an imperfect model becomes a safe feature: high confidence acts, medium confidence asks the customer, low confidence goes to a human. In the full run, no non-opt-out was opted out automatically at 0.90.

### The `max_tokens` truncation bug
My first real run scored 35% recall. I had capped the response length at 60 tokens, and about a quarter of answers were cut off, so the parser fell back to "ambiguous, confidence 0". Raising the cap to 512 removed every parse failure. Lesson: when a result looks bad, check the harness before blaming the model.

### Mislabeled ground truth
I had labeled angry replies like "Who the heck keeps texting me?" as opt-outs. The model called them ambiguous, and on a second read it was right. "Ground truth" is a human decision, and it can be wrong. Relabeling changed the headline number more than any model change.

### Mock vs real evaluation
`--provider mock` runs a hard-coded phrase list. It tests the pipeline without an API key, and its output files carry a `mock_` prefix. Its scores say nothing about model quality, so they must never be cited.

### Synthetic data and its limits
All 450 messages were generated from templates, and the labels came from the same generator. That is cheap and controllable, but results are an upper bound: real messages are messier, and any bias in the generator is shared with the labels. The next steps (hand-labeling a subset blind, adding harder messages) address this.
