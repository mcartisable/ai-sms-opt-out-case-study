# 09. Prompt iterations on the dev split

All numbers here are on the dev split only (275 rows of `data/replies.csv`, 63 rows of `data/hard_cases.csv`), model `claude-haiku-5-5`. The test split is scored once, after the version is frozen; that result is added at the bottom.

What changed in each version is in `prototype/classifier.py` (`VERSIONS`). v1 is the baseline with the old keyword shortcut. v2 and v3 use the strict shortcut (only a bare keyword skips the model) and a longer prompt written from `docs/08-error-analysis.md` and `data/LABELING_POLICY.md`.

## Dev results

| | v1 | v2 | v3 |
|---|---|---|---|
| Recall on non-keyword opt-outs (85 rows) | 91.8% | 97.6% | 100% |
| Main set: correct labels, of 275 | 250 | 254 | 260 |
| Main set: true opt-outs sent to review, of 123 | 7 | 4 | 0 |
| Main set: non-opt-outs sent to review, of 123 | 13 | 9 | 5 |
| Main set: non-opt-outs auto opted out | 0 | 2 | 3 |
| Hard set: correct labels, of 63 | 58 | 53 | 58 |
| Hard set: true opt-outs auto opted out, of 28 | 22 | 20 | 25 |
| Cost per LLM-routed message (hard set) | $0.000082 | $0.000106 | $0.000099 |
| Latency p50 / p95, hard set | 1.3 / 2.4 s | 1.4 / 3.2 s | 1.1 / 2.3 s |

Cost and latency come from one run each and move with the API's load, so treat the differences as noise except that longer prompts cost more input tokens.

## What happened

v2 fixed the slang refusals and deferrals but got worse on the hard set. Two causes: a clause saying `ambiguous` also covers messages that "need an action other than a plain opt-out" sent START, "remove my card" and prompt-injection text to review, and an anger example pulled "Who is this?" into ambiguous. v3 removed that clause and listed questions, commands and order or card requests as `not_opt_out`. It also added that deleting the number or asking for email instead of SMS is an opt-out.

Three versions on dev is where I stopped. Each further edit risks fitting the dev set.

## Remaining dev misses in v3

- Six "Enough already" and "I'm sick of this" messages are labeled `ambiguous` (generator category `frustrated`), and v3 calls them opt-outs. Three reach auto opt-out at 0.90. I think "Enough with the spam already" is a request to stop, so the labels may be wrong. I have not relabeled after seeing predictions. A second labeler should decide.
- "Unsubscribe me from the newsletter" and "Please delete my account" are labeled `ambiguous` in the hard set and reach auto opt-out at 0.90 to 0.97. Whether a newsletter or account request should remove SMS consent is a policy question for compliance.
- Four content-free fragments ("OYE, VALE...", "listen, Awesome") still go to review. Acceptable.
- One prompt-injection string that closes the `<sms>` tag scores 0.4 ambiguous and goes to review, which is the safe outcome.

## Test result (v3, scored once)

| | v1 | v3 |
|---|---|---|
| Recall on non-keyword opt-outs (50 rows) | 42 of 50 (84%, 95% interval 71% to 92%) | 50 of 50 (100%, interval 93% to 100%) |
| Main test set: correct labels, of 175 | 153 | 169 |
| True opt-outs: auto / confirmation / review (of 72) | 55 / 9 / 8 | 66 / 6 / 0 |
| Non-opt-outs auto opted out or sent a confirmation | 0 | 0 |
| Non-opt-outs sent to review (of 90) | 12 | 3 |
| Hard test set: correct labels, of 41 | 36 | 39 |
| Hard test set: true opt-outs auto opted out (of 16) | 16 | 16 |
| Cost per LLM-routed message | | $0.000086 main, $0.000094 hard |
| Latency p50 / p95 | | 0.95 / 2.0 s main, 1.0 / 1.9 s hard |

The three remaining wrong labels on the main test set are the "Maybe later" and "Maybe another time" rows where the hand label said ambiguous and the policy says not_opt_out (see the inconsistency note in `data/LABELING_POLICY.md`). Two more are content-free fragments sent to review. On the hard set, "Cancel my subscription" now reaches the model, which scores opt_out at 0.7, so it triggers a confirmation text instead of an automatic opt-out. That confirms the keyword fix.

## How far to trust this result

100% is a ceiling, not a forecast.
- **The test split is not clean.** I read test misses while writing `docs/08-error-analysis.md`. The consent rule in the v2 and v3 prompts ("never signed up", "never agreed") comes from the labeling policy, and the policy came from a blind sample drawn from the test split. The eight test soft refusals v1 missed were mostly about consent and slang, which the new rules address directly.
- **The data is easy.** Messages are template variants, so one fixed rule fixes a whole family at once. Fifty rows at 100% still allows a true rate near 93%.
- **Labels are mine.** The hard set was labeled by one person in one pass.

What I would claim: v3 fixes the specific failure patterns found in v1, costs about the same, and removes the three-word keyword bug. What I would not claim: 100% recall in production. The fair check is a fresh batch of messages nobody on this project has seen, ideally real replies in shadow mode.
