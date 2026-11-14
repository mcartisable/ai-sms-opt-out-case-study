# 10. LLM judge as a scalable labeler

Question: can a model label messages well enough to replace most hand labeling, so a fresh batch of test messages is cheap? Judge: `claude-sonnet-5-5` (a different, stronger model than the `claude-haiku-5-5` classifier, but from the same vendor, so not fully independent). Code: `prototype/judge.py`. The judge sees only the SMS text, never any label or classifier output.

The tables below are the first run, before the blunt-refusal decision. The rerun with the updated rubric is in the last section.

## Agreement with the blind hand labels (70 English messages)

| Judge rubric | Agreement | Cohen's kappa |
|---|---|---|
| `policy` (the written labeling rules in the prompt) | 91% (64 of 70) | 0.86 |
| `bare` (three one-line definitions, no policy) | 89% (62 of 70) | 0.81 |
| For comparison: the original generator labels vs the same hand labels | 84% | 0.76 |

The judge agrees with the human better than the generator did. The `policy` rubric is partly circular, because the policy was written from those same hand labels, so the `bare` number is the fairer one. Both are in the "substantial to near-perfect" range.

## Agreement with the project labels

| Comparison | n | Agreement | Kappa |
|---|---|---|---|
| Judge (policy) vs `replies.csv` labels | 450 | 93.6% | 0.89 |
| Judge (policy) vs `hard_cases.csv` labels (mine, one pass) | 104 | 96.2% | 0.94 |
| Classifier v3 vs judge, all 554 rows | 554 | 92.4% | 0.87 |
| Classifier v3 vs judge, test split only | 216 | 97.7% | |

Cost of judging all 554 messages: about $0.92 (248k input and 43k output tokens at list prices). That is roughly $0.0017 per message, 20 times the classifier's cost, which is fine for labeling and not for production.

## Where judge and project labels disagree

The judge sends 19 messages I labeled `opt_out` to `ambiguous`:
- 16 are blunt or slang refusals: "get lost already with your promos", "back off already", "I'M DONE WITH THESE TEXTS", "this is getting annoying, enough", "Too many texts, I'm out". This is the same hedge Haiku v1 made. The labeling policy has no rule for blunt refusals, and its anger rule ("anger with no request is ambiguous") pulls the other way. Prompt v3 added the blunt-refusal rule, which is why the classifier now disagrees with the judge on 28 of these rows.
- 3 are "CANCEL SUBSCRIPTION" and "Отпишите меня от рассылки" (unsubscribe me from the mailing). The generator labeled keyword rows like these `opt_out`, while my hard-set policy labels "Cancel my subscription" and "Unsubscribe me from the newsletter" `ambiguous`. The two files disagree with each other.

The judge also agrees with my labels that "Enough already, you're driving me nuts" is `ambiguous`. That is the opposite of what classifier v3 does, which is why those rows reached auto opt-out.

In the reverse direction the judge sends 11 messages to `not_opt_out` that the classifier sends to review, mostly content-free fragments ("SURE LOL") and deferrals.

## What I conclude

- A model can reproduce the hand labels at about the level two careful humans would (kappa 0.8 to 0.9) on these categories. It is good enough to label a fresh batch and to flag doubtful labels.
- It is not good enough to be the final authority. Its rubric decides the edge cases, so the disagreements above are policy gaps, not judge errors.
- Two policy decisions are open (see `data/LABELING_POLICY.md`): whether blunt refusals are opt-outs, and whether "cancel subscription" and "unsubscribe from the newsletter" are opt-outs or ambiguous.

## Limits

Same vendor as the classifier, so shared blind spots are possible (both hedged on the same slang). The 70 hand labels are one person's. The judge with the policy rubric was not validated against a second human.

## After deciding that blunt refusals are opt-outs

I added the decision to the policy and to the judge rubric, then reran the judge on all 554 messages (about $0.94).

| Comparison | Before | After |
|---|---|---|
| Judge (policy) vs blind hand labels, n=70 | 91%, kappa 0.86 | 94%, kappa 0.90 |
| Judge vs `replies.csv` labels, n=450 | 93.6%, kappa 0.89 | 96.0%, kappa 0.93 |
| Judge vs `hard_cases.csv` labels, n=104 | 96.2%, kappa 0.94 | 97.1%, kappa 0.96 |
| Classifier v3 vs judge, all 554 | 92.4%, kappa 0.87 | 96.4%, kappa 0.94 |
| Classifier v3 vs judge, test split (216) | 97.7% | 98.6%, kappa 0.98 |

The gain comes from closing a policy gap, not from a better model. Because the rule now matches the hand labels, the 70-row figure is more circular than before and should not be quoted alone.

Remaining disagreements between classifier v3 and the judge (20 of 554):
- "Enough already, you're driving me nuts" and similar (5 rows): labels and judge say `ambiguous`, classifier v3 says `opt_out` and three reach auto opt-out at 0.90. Prompt v3 treats "enough" as a refusal; the judge reads it as frustration. This is the most important open risk, because it is an automatic action. It needs a prompt change and a fresh test, since v3's test split has been scored.
- "Cancel subscription" and "Unsubscribe me from the newsletter" (6 rows): judge `ambiguous`, classifier `opt_out`. Open policy question 2.
- Content-free fragments such as "OYE, VALE..." (9 rows): judge `not_opt_out`, classifier `ambiguous`. The classifier is more cautious, which costs a little review work and is harmless.

