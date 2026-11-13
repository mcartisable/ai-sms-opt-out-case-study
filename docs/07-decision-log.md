# Decision log

Case study based on my work as a PM at Maestra.io. No real Maestra figures appear here. These are the decisions I would make for the MVP and the reasoning behind them. Numbers are illustrative assumptions, and each decision can be revisited when measured data replaces them. Related: `03-prd.md`, `04-risk-and-compliance.md`, `05-metrics.md`.

| # | Decision | Options | Choice | Rationale | Revisit when |
|---|---|---|---|---|---|
| 1 | Detection approach | LLM prompt; fine-tuned classifier; rules and regex only | LLM prompt with structured output, keywords stay first | Many phrasings and several languages, and there is no labeled training set yet. Rules only would repeat the keyword problem with a longer list. A fine-tuned model needs labels that the review queue will produce later. | Reviewer decisions give enough labeled data, then compare a fine-tuned model on cost and accuracy |
| 2 | Model size | Large model; small cheap model | Small, low-cost model | The task is a three-way label on a short text. Volume is high and latency matters. A larger model is used only to label evaluation data. | Offline recall misses the target in a language |
| 3 | Auto opt-out threshold | 0.80; 0.90; 0.95 | 0.90, per language | Chosen from the cost asymmetry in `04-risk-and-compliance.md` and tuned on calibration data. Illustrative starting point. | Calibration results by language |
| 4 | Confirmation threshold | 0.40; 0.60; 0.75 | 0.60 as the lower bound | A missed opt-out costs more than a confirmation message, so the middle band is wide. | Confirmation reply and false-positive rates |
| 5 | Confirmation SMS | None; confirm every case; confirm the uncertain band | Confirm the uncertain band only | Asking the subscriber is cheap for unclear cases. Confirming clear requests adds friction to someone who already said no. | Legal feedback on the template and markets |
| 6 | Languages | English only; all languages at once; English plus one | English plus one high-volume language, others default to review | Evaluation data and reviewers are needed per language. | Labeled data exists for another language |
| 7 | Build or buy | Build in-house; use an existing vendor or an SMS compliance product | Build the routing, audit and review on the platform, call a hosted model API | The routing and audit log depend on platform data. The model is a replaceable component. I would still check vendors in discovery. | A vendor offers equal accuracy with the required data terms |
| 8 | Data retention | Keep forever; fixed period; nothing stored | Reply text for 24 months (illustrative, legal to confirm), then label, confidence and time only | The brand needs evidence for complaints. Reply text can contain personal data and should not live indefinitely. | Legal review and market requirements |
| 9 | Keyword traps | Route to confirmation now; keep current behavior | Keep current behavior in the MVP | Changing keyword handling carries its own compliance questions. The evaluation set measures the frequency. | Legal agrees and measured frequency is high |
| 10 | Model provider data terms | Default terms; no-retention and no-training terms with regional hosting | No-retention, no-training, regional hosting | Replies can contain personal data. | Provider or brand terms change |
| 11 | Rollout unit | All brands at once; per-brand flag | Per-brand flag, off by default, global kill switch | Brands differ in volume and readiness, and a problem should stay contained. | After the MVP pilot |

## Open decisions

- Whether a pending confirmation pauses all marketing sends or only the triggering campaign.
- How to treat a reply that mixes an opt-out with another request.
- Default action when the review queue is unstaffed past the window, which needs legal input.
