# Integration guide for engineering

Audience: a team that already sends SMS through a provider such as Twilio or Infobip, already receives customer replies, and today honors only keywords (STOP and similar). English only. This folder is the code and the checklist to add natural-language opt-out in front of that, safely, in phases.

Read first: `docs/03-prd.md` (what and why), `docs/04-risk-and-compliance.md` (what can go wrong), `docs/11-fresh-batch.md` (what was actually measured). Everything measured here used synthetic or hand-written English messages. None of it is evidence about your traffic until you run shadow mode.

## What is in the box
| Part | What it does |
|---|---|
| `optout_classifier/core.py` | `OptOutClassifier.decide(text) -> Decision`. Bare-keyword rule, one model call, confidence routing. Never raises: model errors, timeouts, unparseable output and over-long input all return a decision that routes to human review. |
| `optout_classifier/handler.py` | `handle_inbound(...)`: a framework-free example that applies a decision in four rollout modes (shadow, review, confirm, auto) and handles replies to the confirmation text. You implement the `Actions` protocol with your own code. |
| `optout_classifier/shadow.py`, `shadow_report.py` | Log what the classifier would do without doing it, then score the log against human labels. |
| `tests/` | 18 tests, no network, no API key: `cd integration && python3 -m unittest discover -s tests`. They also check the packaged prompt and keyword rule against the prototype. |

## The contract
```python
from optout_classifier import OptOutClassifier
clf = OptOutClassifier()                 # needs ANTHROPIC_API_KEY in the environment; pip install anthropic
d = clf.decide("I don't want your texts anymore")
# Decision(label='opt_out', confidence=0.95, route='auto_opt_out', source='model',
#          model='claude-haiku-5-5', prompt_sha='bebadfae', latency_ms=900, error=None)
```
- `label`: `opt_out`, `not_opt_out` or `ambiguous`. `route`: `auto_opt_out` (confidence 0.90 or more), `send_confirmation` (0.60 to 0.90), `human_review` (anything uncertain, ambiguous, or an error), `no_action`.
- `source`: `keyword`, `model`, `parse_failure`, `error`, `empty` or `too_long`. Store it. A rising share of `error` is an outage signal.
- Always store `model` and `prompt_sha` with the decision. They are your audit trail for "which version decided this".
- The input is one reply. The text is passed to the model inside tags and treated as data, so a reply cannot instruct the classifier.

## Where it sits in your flow
```
inbound reply
  -> your existing keyword matcher (unchanged, authoritative). If it opts the person out, stop here.
  -> if this phone number has a pending confirmation: YES / NO handled by interpret_confirmation_reply()
  -> OptOutClassifier.decide(text)
  -> apply the route according to the current rollout mode
```
Webhook shape differs by provider (check their current docs): Twilio posts form fields such as `From`, `Body` and `MessageSid`; Infobip posts JSON with a `results` list holding fields such as `from`, `text` and `messageId`. Verify the provider's signature, extract those three values, then call `handle_inbound`. Classification adds about one second at the median and about two at p95, so run it asynchronously after you have acknowledged the webhook.

## Roll it out in phases
Set `Mode` per brand, off by default, with a global kill switch that falls back to keywords only.
1. **SHADOW.** Log decisions, change nothing. Run at least two to four weeks. Sample about 300 or more replies at random plus every reply the classifier flagged, have two people label them, and run `python3 integration/shadow_report.py shadow.jsonl --labels labels.csv`. Look at: recall on true opt-outs, true opt-outs ignored (`no_action`), and the share of non-opt-outs it would opt out or ask to confirm.
2. **REVIEW.** Everything that is not `no_action` goes to a person who decides. Measure how often reviewers agree with the classifier.
3. **CONFIRM.** Would-be opt-outs get "Reply YES to unsubscribe". Uncertain cases still go to review.
4. **AUTO.** High-confidence opt-outs happen at once. Enable per brand only after the earlier exits are met.

Exit criteria and numbers to start from are in `docs/05-metrics.md` and `docs/06-rollout-plan.md`. They are illustrative assumptions; replace them with your own after shadow mode.

## What you still have to build
- The `Actions` implementations: suppressing marketing sends, writing an audit record (reply, decision fields, action, time), the confirmation template and its pending state, and a review queue with one-click opt out or keep and a restore action.
- A sending-side check that an opt-out takes effect before the next scheduled send.
- Alerting on `error` and `parse_failure` rates and on model latency; a retry and queueing policy beyond the client's built-in retries (`max_retries=2`, 8 second timeout).
- Per-brand flags, the kill switch and a policy for an unstaffed review queue.

## Known gaps. Do not skip these
- **English only.** Russian and Spanish were generated from templates and are not validated. The keyword rule here is English only.
- **One message at a time.** The classifier does not see the previous outbound message or conversation. This was not evaluated. Replies like "yes", "no" or "who is this?" depend on context. The confirmation flow is handled by rules in `handler.py` for that reason.
- **Measured on synthetic data.** On a fresh unseen batch of 63 messages, 91% of opt-outs were labeled correctly (95% interval 76% to 97%), none was ignored, no harmless message was opted out. Your real replies are messier. Expect worse until you tune on them.
- **Known weak spots.** Frustration such as "Enough already, you're driving me nuts" can reach automatic opt-out at 0.90 while two labelers call it ambiguous. A reply that mixes a stop request with a question goes to review, and nothing stops marketing while it waits. Replies like "delete my account" auto opt-out, which compliance should confirm.
- **Policy is not legal advice.** The decisions in `data/LABELING_POLICY.md` (for example blunt refusals and "cancel my subscription" are opt-outs, wrong number goes to review) need your compliance team's approval, per market.
- **Data handling.** Reply text goes to a model provider. Put no-retention and no-training terms in place first, and keep the shadow log free of text unless reviewers need it (`store_text=False` by default).

## Changing the model or the prompt
Pin the model ID. Any change to the model or prompt means: re-run the evaluation in `prototype/` on your own labeled replies (`prototype/evaluate.py` takes `--data` with your CSV), compare with the previous version, and only then roll out. The prompt in this package is generated from `prototype/classifier.py` by `python3 integration/sync_prompt.py`; do not edit it by hand.

## Install
Copy this folder, or from `integration/`: `pip install .` (Python 3.9 or newer). Set `ANTHROPIC_API_KEY` as a secret in your environment, never in code.
