# Live demo (Cloudflare Pages)

> The public demo now runs on my portfolio: [/work/sms-opt-out-classifier](https://portfolio.temirgaliev.workers.dev/work/sms-opt-out-classifier/). The same `/api/classify` code lives in the portfolio's Worker. This folder still works for running the demo locally.

A static page plus one function, `POST /api/classify`, that runs the same logic as the Python prototype (prompt v3, bare-keyword rule, 0.90 / 0.60 routing). The page works in two modes: recorded answers always, and a "type your own" box when the function is configured.

## How it is protected
- The API key is a Cloudflare secret. It is never in the page, the repo or the browser.
- Messages over 300 characters are rejected. Only same-origin requests are accepted, plus any origin listed in `ALLOWED_ORIGINS`.
- Per-IP limit (default 10 per hour) and a global daily cap (default 300 calls, about 3 cents at current prices), both counted in a KV namespace. The counters are not atomic, so treat the caps as approximate and also set the spend limit below.
- If the key or KV binding is missing, the function answers 503 and the page falls back to recorded examples.
- The text of a message is not logged or stored by this code. It is sent to the Anthropic API for classification, which the page says.

## Test it locally (no key needed)
```bash
cd demo && npm install && npm test          # 15 tests: parity with the Python code, limits, origins, errors
npm run dev                                 # http://localhost:8788 (live box answers "not configured" without a key)
```
After editing `prototype/classifier.py` or the v3 results, run `python3 demo/make_replay.py` from the repo root to refresh the prompt, test fixtures and recorded answers.

## Deploy
1. Cloudflare account (free). In a terminal: `cd demo && npx wrangler login`.
2. `npm run deploy` the first time creates the Pages project `ai-sms-opt-out-demo` and prints its URL.
3. Cloudflare dashboard, Workers & Pages, the project, Settings:
   - Functions, KV namespace bindings: add variable `DEMO_KV`, create a new namespace (any name) and bind it.
   - Variables and Secrets: add secret `ANTHROPIC_API_KEY`. Type it into the dashboard field, not into a chat or a file. Optionally add `DAILY_CAP`, `HOURLY_PER_IP`, `ALLOWED_ORIGINS`.
4. In the Anthropic Console, create a key just for this demo and set a monthly spend limit (for example $5) on it.
5. Redeploy once so the bindings apply: `npm run deploy`.
6. Check: open the URL, try a recorded example, then try your own message; confirm that a view-source search for `sk-ant` finds nothing.

## Later: your Astro portfolio
Link to the deployed URL, embed it in an iframe (add your site's origin to the CSP `frame-ancestors` in `demo/_headers`), or port the page to an Astro page that posts to this endpoint (add your site's origin to `ALLOWED_ORIGINS`).
