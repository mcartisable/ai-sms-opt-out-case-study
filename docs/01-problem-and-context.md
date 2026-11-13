# Problem and context

Case study based on my work as a PM at Maestra.io, a martech platform in the same category as Klaviyo and Attentive. No real Maestra figures appear here. Every number is an illustrative assumption.

## What was true at the time

SMS opt-out on the platform worked on keywords only. A reply of STOP removed the subscriber. Clients also wrote things like "I don't want to receive messages from you anymore" or "please stop texting me", and those people stayed subscribed. The team wanted to handle these replies with AI. This document describes the problem that led to that idea and how I would size it. The solution is in `03-prd.md`.

## Who is affected

**Consumers.** They asked to leave in their own words and kept getting texts. Their next options are a spam report, a complaint to the brand, or blocking the number. Each of those is more effort than the original reply.

**Brands.** They pay for every message sent to someone who already said no. They also carry the legal exposure for ignoring an opt-out, and they see complaint and spam-report rates rise. Their inbound inbox holds these replies, but often nobody reads it.

**The platform.** Brands share sending infrastructure and carrier relationships. One brand with a high complaint rate can lead carriers to filter traffic that other brands also depend on. Support and compliance teams on the platform spend time on cases that a better opt-out flow would not produce.

## How keyword-only fails

The matcher compares a reply with a fixed list (STOP, UNSUBSCRIBE, CANCEL, END, QUIT and local equivalents). It fails in two directions.

1. It misses refusals written as sentences, such as "I've had enough of these texts, delete my number". These stay subscribed.
2. It matches words that appear in unrelated replies. "Don't stop sending me sales" and "can I cancel my Saturday pickup" contain keywords but are not opt-outs. The PRD keeps this behavior in the MVP, and `04-risk-and-compliance.md` explains why.

The first failure is the target of this project. The second is measured and left for a later phase.

## Why it matters

- **Compliance.** US rules and carrier guidelines expect a reasonable opt-out request to be honored, whatever words were used. Other markets have similar principles. Legal review has to confirm the exact obligations per market.
- **Complaints.** A person who cannot leave through the channel they are already using goes to another channel.
- **Carrier filtering.** Carriers watch complaint rates by sender. Filtering hits delivery for every message the brand sends, including ones people want.
- **Wasted spend.** Each message to an unwilling recipient costs money and produces no revenue.

## Illustrative sizing

All inputs below are illustrative assumptions for a single mid-size brand and are not Maestra data.

| Input | Value |
|---|---|
| Messages sent per month (M) | 1,000,000 |
| Reply rate (r) | 2% |
| Share of replies that are opt-out requests (o) | 15% |
| Share of those opt-outs written without a keyword (n) | 35% |
| Cost per message (c) | $0.01 |
| Messages each missed subscriber receives before leaving by another route (k) | 4 |

Formula for missed opt-outs per month:

missed = M × r × o × n = 1,000,000 × 0.02 × 0.15 × 0.35 = 1,050

Wasted spend per month from sending to them:

waste = missed × k × c = 1,050 × 4 × $0.01 = $42

Spend is the small part. Using the false-negative cost from `04-risk-and-compliance.md` (illustrative assumption: $40 per missed opt-out), the exposure is 1,050 × $40 = $42,000 per month. That figure depends on the $40 assumption, which bundles complaint handling, deliverability risk and a share of regulatory exposure, and I would replace it with the brand's own numbers.

Sensitivity: if n is 20% instead of 35%, missed opt-outs fall to 600. If the reply rate is 1%, they fall to 525. The case holds at the low end only if the cost per missed opt-out is above roughly $5 to $10, so that input needs the most scrutiny.

## What to learn next

Every input in the table can be replaced with a measured value from reply logs, which is the first step of `02-discovery.md`. The input I trust least is n, the share of opt-outs written without a keyword.
