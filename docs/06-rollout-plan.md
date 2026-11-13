# Rollout plan

Case study based on my work as a PM at Maestra.io. No real Maestra figures appear here. Durations and thresholds are illustrative assumptions. Metric definitions are in `05-metrics.md`.

## Phases

Each phase runs per brand behind a feature flag that is off by default. A brand moves forward only when the exit criteria hold. A brand can stay at any phase.

**Phase 1: shadow mode (about 2 to 4 weeks).** The classifier labels every non-keyword reply and logs the result. No subscriber is changed and no message is sent. A sample goes to an internal reviewer for comparison.
Exit: offline gate met, shadow recall at or above 85%, error rate and latency within limits, legal sign-off on data handling.

**Phase 2: human review queue (about 4 weeks).** Replies classified as opt-out or unclear appear in the brand's queue with the classifier's suggestion. A person decides. Nothing is automatic.
Exit: reviewers agree with the classifier on more than 90% of cases, median decision time under 24 hours, brand support confirms they can staff the queue.

**Phase 3: confirmation SMS (about 4 weeks).** Opt-out replies at or above the low threshold get "Reply YES to unsubscribe" and marketing sends pause. Unanswered requests go to review after 72 hours (illustrative assumption).
Exit: false positives from confirmation under 2%, no rise in complaint or carrier filtering rate, legal approves the template.

**Phase 4: auto opt-out.** Replies at or above the high threshold (starting at 0.90, illustrative assumption) opt out at once and send the standard confirmation. Lower confidence keeps the phase 3 path. Enabled per language only where offline results justify it.
Exit for expansion: reversal rate under 3% for 4 weeks, guardrails stable.

## Per-client feature flag

Settings per brand: enabled or not, phase, languages, and thresholds (platform-set in the MVP). Every change is logged with who made it. Brands are chosen for early phases when they have high reply volume, an engaged support team and an existing relationship with the account manager.

## Kill switch

A global switch and a per-brand switch both return handling to keyword-only within minutes. They are available to on-call engineers and product. Candidate automatic triggers (illustrative assumptions):

- Reversal rate above 5% over a day for a brand.
- Classifier error or timeout rate above 5% over an hour.
- Complaint rate above 1.5 times the brand's baseline for 3 days.
- Provider outage.

After a trigger, replies still queue for review, so no request is lost.

## Communication to clients

- Before shadow mode: a short note explaining what will be logged and that no behavior changes.
- Before each phase: what changes for their subscribers, what staff must do (for phase 2, review the queue), and how to turn it off.
- A one-page guide with example messages, how to restore a subscriber, and how to export the audit log.
- After each phase: a short summary of results for that brand.

## Support runbook

1. **Subscriber says they were removed by mistake.** Find the decision in the audit log, check reply text and label. Restore with a reason, and confirm with the subscriber if fresh consent is needed (pending legal).
2. **Subscriber says they asked to stop and still got a text.** Find the reply. If the classifier missed it, opt out manually, tag the case for the evaluation set and report it.
3. **Spike in restores or complaints.** Check the guardrails, turn off the brand flag if a threshold is crossed, and notify the product owner.
4. **Review queue backlog.** Notify the brand, and apply the agreed fallback when the window expires.
5. **Provider outage.** Confirm the fallback to keyword-only and queue behavior.

## Risks

| Risk | Mitigation |
|---|---|
| Brands do not staff the review queue | Check staffing before phase 2, alert on queue age |
| Confirmation SMS annoys or breaks rules | Single message, no marketing content, legal review |
| Poor accuracy in a new language | No auto opt-out until per-language data exists |
| Complaint rate moves too slowly to detect harm | Track restores and reviewer overrides as early signals |
| Model or prompt changes shift behavior | Re-run offline evaluation before every change, version everything in the audit log |
