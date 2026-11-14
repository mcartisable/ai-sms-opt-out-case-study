# Hand-labeling guide

Open `blind_sample.csv` in a spreadsheet and fill the `your_label` column for every row. Use `note` for anything you want to remember (optional).

Allowed labels, exactly as written:

- `opt_out`: the sender is clearly asked to stop texting this person, in any wording.
- `not_opt_out`: anything else that is not a request to stop. Questions, thanks, order problems, noise, wrong-number messages that don't ask to stop.
- `ambiguous`: you can't tell whether the person wants to stop.

Rules for a fair test:
1. Label what the message says, as if you were the person reading it at a brand's support desk. Don't guess at what category it came from.
2. Don't open `data/replies.csv` or any results file until you've finished. Those contain the answers.
3. If you hesitate between `opt_out` and `ambiguous`, ask yourself: would you be comfortable removing this person from the list with no further question? If yes, `opt_out`. If you'd want to ask first, `ambiguous`.
4. Don't change earlier labels after seeing later messages. Put a note instead.
5. A quick pass is fine; first instinct is what we want to measure. Rough time: 20-30 minutes.

When done, save the file in the same folder (keep it as CSV) and tell me.
