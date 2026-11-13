# Discovery plan

Case study based on my work as a PM at Maestra.io. This is the discovery approach I used or would use. It contains no findings from real Maestra data, and no quotes. Numbers are illustrative assumptions.

## Questions to answer

1. How many inbound replies are opt-out requests, and how many have no keyword?
2. What do those replies look like, per language?
3. What happens to those subscribers today?
4. What would brands accept as an automated action?

## Sources

**Inbound reply logs.** Sample replies from several brands, stratified by language and by volume. Remove personal data before analysis. Label a sample by hand with two labelers and measure agreement.

**Support tickets.** Search for complaints about messages continuing after a request to stop. Count them and read a sample for context.

**Interviews with CS and compliance.** Six to ten conversations (illustrative assumption). Ask how they handle these replies today, how often someone reads the inbox, what a complaint costs them, and what evidence they need after a removal.

**Brand marketers.** A few short calls on list size, tolerance for wrongful removals, and whether they would enable auto opt-out.

## Reply taxonomy

The taxonomy below is the starting point and gets revised after the first labeling round. `data/replies.csv` is a synthetic stand-in with 450 rows (390 English, 30 Russian, 30 Spanish) and is not real data. Its `category` column uses the same classes.

| Class | Description | Example |
|---|---|---|
| Explicit keyword | Matches the keyword list | "STOP" |
| Soft refusal | Clear opt-out in a sentence | "I don't want to receive messages from you anymore" |
| Frustrated | Opt-out with anger or profanity | "Stop spamming me" |
| Keyword trap | Contains a keyword, not an opt-out | "Don't stop sending me sales" |
| Ambiguous | Could mean pause or leave | "Maybe later" |
| Wrong number or other | Wrong recipient, deceased, changed owner | "Wrong number" |
| Other language | Any class in a language outside the main set | A Russian or Spanish refusal |
| Not opt-out | Question or positive reply | "Does the code work on sale items?" |

Ambiguous replies and wrong-number replies are the hard ones to label, so the guideline for labelers must say what to do with them. In the synthetic file, ambiguous rows are labeled `ambiguous` and wrong-number rows sit in `wrong_number_or_other`.

## Jobs to be done

- **Consumer:** "When I get texts I no longer want, I want to stop them with one reply in my own words, so I do not have to find another way."
- **Brand marketer:** "When someone wants to leave, I want them removed fast and cleanly, so my complaint rate stays low and I keep the subscribers who are willing."
- **Compliance or support at the brand:** "When a complaint arrives, I want a record of what the person wrote and what we did, so I can answer within the deadline."
- **Platform:** "When many brands share our sending routes, I want every brand to honor opt-outs, so carriers keep trusting our traffic."

## Hypotheses and tests

| Hypothesis | Test | Would change the plan if |
|---|---|---|
| Non-keyword opt-outs are a meaningful share of all opt-outs | Count in the labeled log sample | Share is under about 10% (illustrative assumption) |
| Brands do not read the inbound inbox quickly | Interviews, plus time-to-first-read in logs if available | Most brands answer within hours |
| A classifier reaches high recall on soft refusals with low false opt-outs | Offline evaluation on the labeled set (see `05-metrics.md`) | Recall is low in the main language |
| A confirmation SMS resolves most unclear cases | Shadow data, then pilot | Few people answer |
| Brands will accept auto opt-out above a high threshold | Interviews, pilot opt-in rate | Most brands demand human approval |
| Keyword traps are common enough to matter | Count in the labeled sample | They exceed opt-outs missed |

## Output

A labeled set with a labeling guideline, an input table for the sizing in `01-problem-and-context.md` using measured values, and a go or no-go recommendation for shadow mode, defined in `06-rollout-plan.md`.
