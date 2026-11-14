# 11. Fresh batch: one unbiased run of prompt v3

Why: the v3 test result (100% recall on opt-outs with no keyword) came from a split I had partly read, so it was a ceiling, not an estimate. This batch is the fair check.

## How it was run
- 65 new English messages, written by me before any model saw them (`data/make_fresh_cases.py`, committed before any run). They are my writing, so they still miss how real customers write.
- Labels were fixed before the classifier ran (`data/finalize_fresh.py`): your blind label where it exists (25 rows), else the judge and my intent agreeing (38 rows), else the row is disputed and skipped (2 rows: "How did you even get my number?" and "Enough already, I swear"). 63 rows scored.
- Prompt v3, `claude-haiku-5-5`, scored once, unchanged. Judge: `claude-sonnet-5-5`, kappa 0.68 against your 25 blind labels and 0.93 against my intent.

## Result (final labels, 63 rows)

| | v3 on fresh batch |
|---|---|
| Correct labels | 59 of 63 (kappa 0.90) |
| True opt-outs (34): opted out automatically | 26 |
| True opt-outs: sent a confirmation text | 4 |
| True opt-outs: sent to human review | 4 |
| True opt-outs: ignored | 0 |
| Opt-outs the model labeled `opt_out` | 30 of 34 (88%, 95% interval 73% to 95%) |
| Non-opt-outs opted out or sent a confirmation | 0 of 29 |
| Real `not_opt_out` messages (20) sent to review | 0 |
| Cost per message / latency p50, p95 | $0.00009 / 0.9 s, 2.2 s |

The 100% on the older test split was too high. On messages nobody had seen, recall as a label is 88% with a wide interval, but the routing still caught every opt-out: none was ignored, and nothing harmless was opted out.

## The four misses
- "I'm so sick of this", "I think you have the wrong number", "This number is not Maria's anymore" (3 rows): your blind label says `opt_out`. The policy says `ambiguous`, and v3 followed the policy, so these went to human review. This is a conflict between your instinct and the written rule, not a model slip.
- "Hi, quick one: where's my parcel? And also I'd like you to stop texting me promos." (1 row): a real model miss. The parcel question diluted the request, and the model scored it ambiguous at 0.6. It went to human review.

Under my stricter policy labels (my intent, not your blind labels) the result is 60 of 63 correct, 24 of 29 opt-outs automatic, 4 confirmations and 1 to review. The two rows where this differs are "Please delete my account and my data" and "How do I unsubscribe from the newsletter?", which v3 opted out automatically at 0.90 and 0.95 while my intent said ambiguous. You and the judge both called the second one an opt-out.

## What it means
- v3 is a good classifier on these message styles, not a perfect one. A fair claim is "roughly 88% to 100% label recall, with routing that ignored none".
- The biggest question is policy, not the model: wrong-number replies and account-deletion requests. Your blind labels remove the person; the policy sends them to a human. Decided by the product owner: wrong-number replies stay in human review, so the policy and prompt v3 stand.
- The "Enough already" risk from the dev analysis is not resolved here. The two relevant rows ended up disputed and were skipped. One related row, "enough with the texts already", was a consensus opt-out and v3 got it right.
- A buried request next to a different question is a real weakness to fix in a later prompt version.

## Limits
Sixty-three messages is small, and 34 opt-outs gives a wide interval. All messages are mine. The labels use 25 human rows, 38 consensus rows and no second human.
