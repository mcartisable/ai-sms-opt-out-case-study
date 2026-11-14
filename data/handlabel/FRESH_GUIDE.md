# Hand-labeling guide for the fresh batch (25 messages)

Open `fresh_blind_sample.csv` in a spreadsheet and fill `your_label` for every row. `note` is optional.

Allowed labels, exactly as written:

- `opt_out`: the sender is clearly asked to stop texting this person, in any wording.
- `not_opt_out`: anything else that is not a request to stop.
- `ambiguous`: you can't tell whether the person wants to stop.

Rules for a fair test:
1. Label what the message says, as if you were reading it at a brand's support desk. Use your own judgment, not what you remember of the project's labeling policy.
2. Don't open `data/fresh_cases.csv`, any results file or any judge report until you've finished. They contain answers.
3. Don't change earlier labels after seeing later messages. Put a note instead.
4. First instinct is what we want. About 10 minutes.

Save as CSV in the same folder and tell me.
