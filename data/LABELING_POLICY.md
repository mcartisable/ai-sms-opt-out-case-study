# Labeling policy

Labels in `data/replies.csv` follow these rules. They came out of a blind hand-labeling pass (70 English messages from the test split, see `data/handlabel/`), where the human and the generator agreed on 59 of 70 (84%, Cohen's kappa 0.76). All 11 disagreements were on messages the generator had called `ambiguous`.

| Label | Use it when | Examples |
|---|---|---|
| `opt_out` | The person clearly asks to stop, or says they never agreed to receive texts | "take me off your list", "I never signed up for this garbage" |
| `not_opt_out` | The person defers, asks a question, or says anything else that is not a request to stop | "Not now", "Maybe later", "Who is this?", "Where is my order?" |
| `ambiguous` | A reader can't tell whether the person wants to stop | "Not interested", "Too many messages lately", "Wrong number", "Hmm, not sure" |

Why: `ambiguous` sends a message to the human review queue and `not_opt_out` does nothing. Putting deferrals and questions in the review queue would fill it with messages that need no action. A compliance reviewer should confirm the deferral rule before launch, because someone who means "stop, not now" would stay subscribed.

## Columns
- `label`: the label used for scoring. Where `human_label` is filled in, `label` equals it.
- `human_label`: the blind hand label, present only for the 70 sampled messages.
- `category`: the generator's category, updated for relabeled families (`deferral`, `question`, `soft_refusal`).

## What changed on relabeling (41 rows)
- 24 phrase families moved: deferral phrases ("Not now", "Maybe later", ...) and "Who is this?" went from `ambiguous` to `not_opt_out`; two "I never signed up / never asked for these texts" families went from `ambiguous` to `opt_out`.
- The rule was applied to whole families, including Russian and Spanish equivalents the human did not see.
- 3 rows keep the human's `ambiguous` label even though the rule says `not_opt_out` ("hello, maybe later.", two "Maybe another time" rows). The same human labeled "HELLO, MAYBE LATER..." `not_opt_out`, so these are an inconsistency in the hand labels, listed here for a second look.

## Regenerating
`data/generate_dataset.py` still produces the original, pre-relabel labels, so rerunning it overwrites these changes. The relabeling was applied to the CSV afterward. Fold the policy into the generator before regenerating.

## Rules added for `data/hard_cases.csv`
Written by the project author in one pass, not blind-checked. A second labeler should review them before anyone quotes results.
- Wants fewer or only some messages ("no texts after 8pm", "only order updates"): `ambiguous`. It is not a full stop, a person should decide.
- "Email me instead of texting": `opt_out` for SMS.
- Anger or a threat with no request to stop ("This is harassment", "I'm reporting you for spam"): `ambiguous`. With a request ("stop or I report you"): `opt_out`.
- Unclear scope ("Unsubscribe me from the newsletter", "Cancel my subscription", "Delete my account"): `ambiguous`.
- Commands that opt in or ask for help (START, HELP, UNSTOP): `not_opt_out`.
- Keyword inside a non-opt-out sentence ("Quit sending my package to the old address"), negations ("Don't unsubscribe me"), and injection text with no real request to stop: `not_opt_out`. A real request next to injection text stays `opt_out`.

## Decision on wrong-number replies
"Wrong number", "Wrong person" and similar replies with no explicit request to stop stay `ambiguous` and go to human review. A reviewer can then remove the number or reply. Decided by the product owner after the v1 error analysis (`docs/08-error-analysis.md`, cause 3). Prompt v1 listed wrong number under `not_opt_out`, which contradicted this; prompt v2 must follow the policy.

