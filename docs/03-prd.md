# PRD: AI-assisted SMS opt-out

Case study based on my work as a PM at Maestra.io, a martech platform in the same category as Klaviyo and Attentive. The product details are reconstructed for a portfolio. No real Maestra figures appear here. Every number is marked as an illustrative assumption.

## Mock press release

**Maestra now recognizes opt-out requests written in plain language**

Brands on Maestra send SMS campaigns to millions of subscribers. Until now, a subscriber had to reply with a keyword such as STOP to leave a list. People who wrote "please stop texting me" or "I don't want these messages anymore" kept receiving texts, and many of them complained to the brand or reported the number as spam.

Starting today, brands can turn on natural-language opt-out. Keyword rules still run first. Replies without a keyword are read by a classifier that decides whether the person is asking to leave. Clear requests are honored at once. Unclear ones get a short confirmation text ("Reply YES to unsubscribe") or go to a review queue. Every decision is logged and can be reversed.

"We used to see angry replies sitting in our inbox for days," said a marketing lead at a pilot brand (fictional quote). "Now those people are off the list the same day, and our spam reports went down."

## Problem statement

The opt-out pipeline matches a fixed keyword list: STOP, UNSUBSCRIBE, CANCEL, END, QUIT and local equivalents. Subscribers often write a full sentence instead. Those replies land in the brand's inbound inbox, where nobody may read them, and the subscriber stays on the list.

Subscribers who asked to leave keep getting messages. Carriers watch complaint rates and may filter a brand's traffic. Regulators and carrier guidelines in several markets expect a reasonable opt-out request to be honored, whatever words were used.

## Target users

- **End consumers.** People receiving brand SMS. They want to stop messages by replying however they naturally write.
- **Brand marketers.** They own SMS revenue and list size. They want to keep willing subscribers and avoid deliverability damage.
- **Compliance and customer support at the brand.** They handle complaints and need evidence of when and why a subscriber was removed.
- **Platform (Maestra).** Shared sending infrastructure and carrier reputation depend on every brand's opt-out handling.

## Goals

1. Honor opt-out intent expressed without a keyword, in the languages the brand sends in.
2. Keep wrongful removals of willing subscribers low and recoverable.
3. Give brands an audit trail for every automated decision.
4. Let each brand choose whether to enable the feature and how strict it is.

## Non-goals

- Classifying other intents (order status, complaints, product questions) in this release.
- Replying to subscribers with generated text. The only outbound message is a fixed confirmation template.
- Changing how keyword opt-out works today.
- Email or push channels.

## Solution

Inbound replies pass through three tiers.

**Tier 1: keyword rules.** The existing matcher runs first and stays authoritative. A keyword match opts the subscriber out exactly as today. The classifier never sees these messages.

**Tier 2: LLM classifier.** Non-keyword replies are sent to a classifier that returns one label from a fixed set (`opt_out`, `not_opt_out`, `unclear`) and a confidence score. The prompt includes the reply and, where available, the last outbound message for context. It excludes subscriber profile data.

**Tier 3: routing by confidence.**

| Classifier result | Action |
|---|---|
| `opt_out`, confidence at or above the high threshold | Opt out immediately, send the standard opt-out confirmation |
| `opt_out` between the low and high thresholds, or `unclear` | Send "Reply YES to unsubscribe" and pause marketing sends until a reply or a timeout |
| Below the low threshold, or edge cases flagged by rules | Add to the brand's human review queue |
| `not_opt_out`, high confidence | No change |

Starting thresholds (illustrative assumption): auto opt-out at 0.90, confirmation between 0.60 and 0.90. Thresholds are tuned on a labeled set before launch and per language afterward. The reasoning for setting them asymmetrically is in `04-risk-and-compliance.md`.

**Supporting capabilities**

- **Audit log.** Each decision stores the reply text, the label, confidence, model and prompt version, the action taken and a timestamp.
- **Reversibility.** A brand admin can restore a subscriber removed by the classifier. Restoring requires a reason and is logged. It does not apply to keyword opt-outs.
- **Per-client enablement.** The feature sits behind a feature flag per brand, off by default, with a global kill switch.
- **Multilingual support.** The classifier handles every language the brand sends in. Languages without enough evaluation data default to confirmation or review instead of auto opt-out.

## Functional requirements

1. Keyword matching runs before the classifier on every inbound reply.
2. The classifier returns only a label from the fixed set and a numeric confidence. Any other output is treated as `unclear`.
3. Auto opt-out takes effect before the next scheduled send to that subscriber.
4. The confirmation SMS uses a fixed, brand-editable template with no generated text.
5. If the subscriber does not answer the confirmation within a set window (illustrative assumption: 72 hours), the request goes to the review queue.
6. The review queue shows reply text, classifier output and the preceding outbound message, with one-click opt out or keep.
7. All decisions are written to the audit log and exportable by the brand.
8. Classifier timeouts or errors route the reply to the review queue.

## Open questions

- Should the pause during a pending confirmation cover all marketing sends or only the campaign that triggered the reply?
- How do we handle a reply that contains both an opt-out and an order question?
- What review-queue response time can brands realistically staff for?
- Do some markets require an opt-out to be honored without a confirmation step at any confidence level?

## Success metrics

Primary metric: share of non-keyword opt-out requests honored within 24 hours. Guardrails: wrongful opt-out rate, restore rate, and spam complaint rate. Definitions, baselines and targets are in `docs/05-metrics.md`.

## Phased scope

**MVP**
- Three-tier flow for English and one additional high-volume language.
- Fixed thresholds per language, set by the platform.
- Audit log, restore action, review queue, feature flag, kill switch.
- Pilot with a small group of brands (illustrative assumption: 5 to 10).

**Later**
- Brand-configurable thresholds and more languages.
- Using reviewer decisions as labeled data to retrain or recalibrate.
- Detecting other intents, such as support requests, and routing them to the brand's helpdesk.
