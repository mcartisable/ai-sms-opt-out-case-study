# Judge report: rubric `policy`, model `claude-sonnet-5-5`, rows 65

Judge parse failures: 0. Prompt hash: `5428cf01`.

| comparison | n | agreement | Cohen's kappa |
|---|---|---|---|
| judge vs hand label (blind, human) | 25 | 0.840 | 0.68 |
| judge vs author label, fresh_cases.csv | 65 | 0.954 | 0.93 |

### judge vs hand label (blind, human) (rows = truth)

| truth \ judge | opt_out | not_opt_out | ambiguous | parse_failure |
|---|---|---|---|---|
| opt_out | 15 | 0 | 4 | 0 |
| not_opt_out | 0 | 5 | 0 | 0 |
| ambiguous | 0 | 0 | 1 | 0 |

### judge vs author label, fresh_cases.csv (rows = truth)

| truth \ judge | opt_out | not_opt_out | ambiguous | parse_failure |
|---|---|---|---|---|
| opt_out | 29 | 0 | 0 | 0 |
| not_opt_out | 0 | 20 | 0 | 0 |
| ambiguous | 2 | 1 | 13 | 0 |

### Disagreements to adjudicate (hard cases, and hand-labeled rows)

| id | category | text | project label | hand label | judge | judge's reason |
|---|---|---|---|---|---|---|
| 2023 | frustrated | I'm so sick of this | ambiguous | opt_out | ambiguous | The person expresses frustration but does not clearly ask to stop the texts or tell the sender to go away. |
| 2041 | wrong_number | I think you have the wrong number | ambiguous | opt_out | ambiguous | Saying it's the wrong number doesn't clearly say whether they want the texts to stop. |
| 2043 | wrong_number | This number is not Maria's anymore | ambiguous | opt_out | ambiguous | This is a wrong-number notice with no clear request to stop the texts. |
| 2063 | account | Please delete my account and my data | ambiguous | opt_out | ambiguous | The person asks to delete their account and data but never says they want the texts to stop, so the scope is unclear. |

Tokens of all judged rows (input/output): 34373 / 3994, about $0.109 at the table prices.
