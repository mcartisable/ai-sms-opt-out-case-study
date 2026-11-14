# 08. Error analysis of prompt v1

Prompt v1 (hash `fc095f5b`) on `claude-haiku-5-5`. Sources: all 450 rows of `data/replies.csv` (47 label mismatches) and the 41 test rows of `data/hard_cases.csv` (5 mismatches). The 63 dev rows of the hard set are not scored yet.

Method: read every miss, write one sentence on why it happened (open coding), then group the sentences into causes (axial coding). Near-duplicates of one phrase count once and show their row count.

## One rule for using this file

I read test-split misses to write this. That makes the test split slightly seen. Prompt v2 may only be changed because of dev examples, and the test split is then scored once. I mark each code with its split so this can be checked. Examples that only appear in test are used to describe problems, not to write prompt text.

## Open codes

### Real opt-outs the model hedged on (15 rows, 8 phrases, all routed to human review at 0.6 to 0.7)

| # | Phrase | Rows | Split | Why it was missed |
|---|---|---|---|---|
| 1 | "I never asked for these texts" / "I did not agree to get texts from you" | 4 | test | A complaint about consent with no verb like stop or remove, so the model read it as a complaint, not a request. |
| 2 | "Idiots, I never signed up for this garbage" | 3 | test | Same consent complaint, plus anger, which the model scores as "unclear what they want". |
| 3 | "this is getting annoying, enough" | 2 | dev | "Enough" means stop, but the prompt calls vague dissatisfaction ambiguous, so the model hedged. |
| 4 | "I'M DONE WITH THESE TEXTS" | 1 | dev | "Done with" is a clear stop, but the same vague-dissatisfaction rule applied. |
| 5 | "Too many texts, I'm out" | 1 | test | "Too many messages" is the example the prompt gives for ambiguous, so the model copied the example. |
| 6 | "what the hell, back off already :)" | 1 | dev | An idiom plus a smiley, so the model discounted the anger. |
| 7 | "get lost already with your promos" | 3 | dev | An idiom for stop; the model had no rule for slang refusals. |

### Non-opt-outs sent to review (25 rows)

| # | Phrase | Rows | Split | Why |
|---|---|---|---|---|
| 8 | Deferrals: "Not now", "Maybe later", "Check back in a month" | 20 | both | The labeling policy says deferrals need no action, but the prompt never says so, and "unclear whether they want to stop" fits them. |
| 9 | Fragments: "SURE LOL", "Listen, ok cool", "OYE, VALE..." | 4 | both | No content to judge, so 0.5 to 0.6 and review. Arguably correct behavior. |
| 10 | "Sí, por favor..." (yes please) | 1 | dev | The trailing ellipsis made a plain yes read as reluctant. |

### Ambiguous messages the model treated as harmless (6 rows, no action taken)

| # | Phrase | Rows | Split | Why |
|---|---|---|---|---|
| 11 | "Wrong number.", "Wrong person pls", "Непарвильный номер!!" | 4 | both | The prompt lists wrong number under not_opt_out, while the policy says ambiguous. The prompt and the policy disagree, and the model followed the prompt. |
| 12 | "Who the hell gave you my number :)" | 1 | test | The smiley lowered the anger; no request to stop, so not_opt_out at 0.7. |
| 13 | "Ok so holy crap, another promo? really? :)" | 1 | dev | Same: a smiley turned frustration into casual chat. |

### One false positive

| # | Phrase | Rows | Split | Why |
|---|---|---|---|---|
| 14 | "Quit it with the flash sales lol, my wallet hurts :)" | 1 | dev | Scored opt_out at 0.75, so it only triggered a confirmation text. My label (not_opt_out, keyword trap) is the doubtful part: this reads as a request to stop the promos. |

### Hard set, test half (5 rows)

| # | Phrase | Split | Why |
|---|---|---|---|
| 15 | "Cancel my subscription" | test | Not a model error. The hybrid rule treats any message of three words or fewer containing a keyword as final, so it was opted out at 0.99 without the model seeing it. "Cancel my order" and "Quit your job" would be opted out the same way. |
| 16 | "Please only text me on weekdays", "Cut it down to one text a month" | test | The model sees no request to stop and returns not_opt_out. My label (ambiguous) came from my own policy, which treats a preference change as needing a person. The prompt doesn't mention preference changes. |
| 17 | "Who is Daniel? He doesn't have this number anymore" | test | A wrong-number case at 0.93 not_opt_out. Same cause as #11. |
| 18 | "Remove me from the waitlist for the jacket" | test | Sent to review at 0.6. The model was cautious about "remove me"; my label (not_opt_out) is defensible, and so is the model. |

## Grouped causes

1. **The prompt's own rule makes the model hedge on slang and impatience (#3, #4, #5, #6, #7, 11 rows).** The "vague dissatisfaction is ambiguous" line and its examples pull clear refusals down to 0.6. Fix: say that impatient or slang refusals ("enough", "back off", "get lost", "I'm done with these") are opt-outs.
2. **The prompt lacks the labeling policy (#1, #2, #8, #11, 29 rows).** Consent complaints, deferrals and wrong-number replies each have a policy answer that the prompt never states. Fix: put those three rules in the prompt, with one example each.
3. **Wrong number is the risky direction (#11, #17, 5 rows).** These customers stay subscribed with no human ever looking. Decision (product owner): wrong-number replies go to human review, which matches the existing labeling policy. The prompt, not the policy, was wrong. Prompt v2 must say so.
4. **Tone cues move the score (#6, #12, #13).** Smileys and "lol" make the model treat anger as friendly. Low priority and only 3 rows.
5. **A design bug, not a model error (#15).** Fix in code: apply the keyword shortcut only to a bare keyword ("STOP", "STOP please"), not any short message with a keyword in it.
6. **Doubtful labels (#14, #16, #18).** Three or four rows where my label may be wrong. A second labeler should decide before these count as model errors.
7. **Acceptable behavior (#9, #10).** Messages with no content deserve review. No fix.

## What this changes for prompt v2

Edit the prompt for causes 1 and 2, using dev examples only. Fix the keyword shortcut in code (cause 5). Wrong number is decided: human review, so v2 states `ambiguous` for it (cause 3). Leave causes 4, 6 and 7 alone for now.

The change that matters most is #8: 20 of the 25 wasted review items are deferrals. The one that matters most for compliance is #11: those replies get no action at all.
