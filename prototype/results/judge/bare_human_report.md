# Judge report: rubric `bare`, model `claude-sonnet-5-5`, rows 70

Judge parse failures: 0. Prompt hash: `05cf7829`.

| comparison | n | agreement | Cohen's kappa |
|---|---|---|---|
| judge vs hand label (blind, human) | 70 | 0.886 | 0.81 |
| judge vs project label, replies.csv | 70 | 0.886 | 0.81 |

### judge vs hand label (blind, human) (rows = truth)

| truth \ judge | opt_out | not_opt_out | ambiguous | parse_failure |
|---|---|---|---|---|
| opt_out | 24 | 0 | 3 | 0 |
| not_opt_out | 0 | 31 | 3 | 0 |
| ambiguous | 0 | 2 | 7 | 0 |

### judge vs project label, replies.csv (rows = truth)

| truth \ judge | opt_out | not_opt_out | ambiguous | parse_failure |
|---|---|---|---|---|
| opt_out | 24 | 0 | 3 | 0 |
| not_opt_out | 0 | 31 | 3 | 0 |
| ambiguous | 0 | 2 | 7 | 0 |

### Disagreements to adjudicate (hard cases, and hand-labeled rows)

| id | category | text | project label | hand label | judge | judge's reason |
|---|---|---|---|---|---|---|
| 10 | deferral | hello, maybe later. | ambiguous | ambiguous | not_opt_out | The customer is putting off an offer ('maybe later') and does not ask to stop receiving messages. |
| 91 | deferral | Not now thx | not_opt_out | not_opt_out | ambiguous | "Not now thx" could mean a temporary decline of the current offer or a wish to stop messages, so intent to opt out is unclear. |
| 172 | deferral | Not now pls | not_opt_out | not_opt_out | ambiguous | "Not now pls" could mean pausing or declining the current offer, or it could mean they want messages to stop, so intent is unclear. |
| 189 | soft_refusal | Idiots, I never signed up for this garbage. | opt_out | opt_out | ambiguous | The person is angry and says they never signed up, which suggests they don't want the messages, but they don't explicitly ask to stop. |
| 202 | soft_refusal | Idiots, i never signed pu for this garbage!! | opt_out | opt_out | ambiguous | The customer is angry and says they never signed up, which implies they don't want the messages, but they don't explicitly ask to stop. |
| 223 | deferral | HELLO, MAYBE LATER... | not_opt_out | not_opt_out | ambiguous | "Maybe later" signals a deferral and not a clear request to stop messages, so the person's wish to opt out is unclear. |
| 326 | soft_refusal | IDIOTS, I NEVER SIGNED UP FOR THIS GARBAGE pls | opt_out | opt_out | ambiguous | The customer is angry and says they never signed up, but they don't explicitly ask to stop receiving messages. |
| 388 | deferral | Maybe another time | ambiguous | ambiguous | not_opt_out | The customer is politely declining the current offer for now, but does not ask to stop receiving messages. |

Tokens of all judged rows (input/output): 15826 / 5474, about $0.086 at the table prices.
