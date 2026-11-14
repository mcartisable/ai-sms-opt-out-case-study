# Decision log

Case study based on my work as a PM at Maestra.io. No real Maestra figures appear here. These are the decisions I would make for the MVP and the reasoning behind them. Numbers are illustrative assumptions, and each decision can be revisited when measured data replaces them. Related: `03-prd.md`, `04-risk-and-compliance.md`, `05-metrics.md`.

| # | Decision | Options | Choice | Rationale | Revisit when |
|---|---|---|---|---|---|
| 1 | Detection approach | LLM prompt; fine-tuned classifier; rules and regex only | LLM prompt with structured output, keywords stay first | Many phrasings and several languages, and there is no labeled training set yet. Rules only would repeat the keyword problem with a longer list. A fine-tuned model needs labels that the review queue will produce later. | Reviewer decisions give enough labeled data, then compare a fine-tuned model on cost and accuracy |
| 2 | Model size | Large model; small cheap model | Small, low-cost model (`claude-haiku-5-5` in the prototype) | The task is a three-way label on a short text. Volume is high and latency matters. Measured in the prototype: about $0.00009 per message and p95 about 2.2 s. A larger model (`claude-sonnet-5-5`, about 20 times the cost per message) is used only to label evaluation data, where its agreement with blind human labels was kappa 0.81 to 0.90. | Offline recall misses the target in a language |
| 3 | Auto opt-out threshold | 0.80; 0.90; 0.95 | 0.90, per language | Chosen from the cost asymmetry in `04-risk-and-compliance.md` and tuned on calibration data. Illustrative starting point. | Calibration results by language |
| 4 | Confirmation threshold | 0.40; 0.60; 0.75 | 0.60 as the lower bound | A missed opt-out costs more than a confirmation message, so the middle band is wide. | Confirmation reply and false-positive rates |
| 5 | Confirmation SMS | None; confirm every case; confirm the uncertain band | Confirm only the `opt_out` replies in the uncertain confidence band; `ambiguous` goes to review | Asking the subscriber is cheap when the model thinks they want out but is not sure. Confirming clear requests adds friction to someone who already said no. | Legal feedback on the template and markets |
| 6 | Languages | English only; all languages at once; English plus one | English plus one high-volume language, others default to review | Evaluation data and reviewers are needed per language. | Labeled data exists for another language |
| 7 | Build or buy | Build in-house; use an existing vendor or an SMS compliance product | Build the routing, audit and review on the platform, call a hosted model API | The routing and audit log depend on platform data. The model is a replaceable component. I would still check vendors in discovery. | A vendor offers equal accuracy with the required data terms |
| 8 | Data retention | Keep forever; fixed period; nothing stored | Reply text for 24 months (illustrative, legal to confirm), then label, confidence and time only | The brand needs evidence for complaints. Reply text can contain personal data and should not live indefinitely. | Legal review and market requirements |
| 9 | Keyword traps | Route to confirmation now; keep current behavior; bare-keyword rule | Production keeps current behavior in the MVP. The prototype and shadow mode measure the bare-keyword rule | Changing keyword handling carries its own compliance questions. The prototype showed that treating any short message containing a keyword as final opts out "Cancel my subscription" and similar replies with no check. | Legal agrees and shadow mode shows how often keyword-in-sentence replies occur |
| 10 | Model provider data terms | Default terms; no-retention and no-training terms with regional hosting | No-retention, no-training, regional hosting | Replies can contain personal data. | Provider or brand terms change |
| 11 | Rollout unit | All brands at once; per-brand flag | Per-brand flag, off by default, global kill switch | Brands differ in volume and readiness, and a problem should stay contained. | After the MVP pilot |

| 12 | Labeling policy as a product decision | Let the model decide edge cases; write the rules down | Written policy in `data/LABELING_POLICY.md`, changed only by an explicit decision | Edge cases decide review workload and compliance exposure. Decisions so far: blunt refusals, "never signed up" and "cancel my subscription" are opt-outs; deferrals need no action; wrong number and anger with no request go to review. | Compliance review or real-reply data |
| 13 | How a prompt change is accepted | Edit and ship; tune on dev and score a held-out split once | Tune on a dev split, score the held-out split once per version, disclose anything seen | Three prompt versions were tried on dev. Version 2 got worse on the hard set and was dropped. A fresh batch then cut the claimed 100% recall to 88%. | A larger real-reply set exists |

## Open decisions

- Whether a pending confirmation pauses all marketing sends or only the triggering campaign.
- How to treat a reply that mixes an opt-out with another request.
- Default action when the review queue is unstaffed past the window, which needs legal input.
- Whether account-deletion requests remove SMS consent, and how to handle "Enough already" style frustration that prompt v3 may opt out automatically.
