// Cloudflare Pages Function: POST /api/classify  {"text": "..."} -> {label, confidence, source, route}
// Secrets and bindings (see demo/README.md): ANTHROPIC_API_KEY (secret), DEMO_KV (KV namespace),
// optional vars: ALLOWED_ORIGINS (comma list, in addition to same-origin), DAILY_CAP, HOURLY_PER_IP.
// The message text is never logged or stored.
import { MODEL, classify } from "../_shared/classifier.js";

const MAX_CHARS = 300;
const json = (body, status = 200, extra = {}) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", "cache-control": "no-store", ...extra } });

function allowedOrigin(request, env) {
  const origin = request.headers.get("origin");
  if (!origin) return null;
  const self = new URL(request.url).origin;
  const extra = (env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
  return origin === self || extra.includes(origin) ? origin : false;
}

async function bump(kv, key, ttl) {
  const n = parseInt((await kv.get(key)) || "0", 10) + 1; // not atomic; good enough as an approximate cap
  await kv.put(key, String(n), { expirationTtl: ttl });
  return n;
}

export async function onRequest({ request, env }) {
  const origin = allowedOrigin(request, env);
  const cors = origin ? { "access-control-allow-origin": origin, vary: "origin" } : {};
  if (request.method === "OPTIONS") {
    return new Response(null, { status: origin ? 204 : 403, headers: { ...cors, "access-control-allow-methods": "POST", "access-control-allow-headers": "content-type" } });
  }
  if (request.method !== "POST") return json({ error: "Use POST." }, 405);
  if (origin === false) return json({ error: "Origin not allowed." }, 403);
  if (!env.ANTHROPIC_API_KEY || !env.DEMO_KV) return json({ error: "The live demo is not configured. The recorded examples still work." }, 503, cors);
  if (!(request.headers.get("content-type") || "").includes("application/json")) return json({ error: "Send JSON." }, 415, cors);

  let text;
  try { ({ text } = await request.json()); } catch { return json({ error: "Invalid JSON." }, 400, cors); }
  if (typeof text !== "string" || !text.trim()) return json({ error: "Send a non-empty text." }, 400, cors);
  if (text.length > MAX_CHARS) return json({ error: "Keep it under " + MAX_CHARS + " characters." }, 413, cors);

  const dailyCap = parseInt(env.DAILY_CAP || "300", 10), perIp = parseInt(env.HOURLY_PER_IP || "10", 10);
  const now = new Date(), day = now.toISOString().slice(0, 10), hour = now.toISOString().slice(0, 13);
  const ip = request.headers.get("cf-connecting-ip") || "unknown";
  if ((await bump(env.DEMO_KV, "ip:" + ip + ":" + hour, 3700)) > perIp) return json({ error: "Too many tries from your network this hour. The recorded examples still work." }, 429, cors);
  if ((await bump(env.DEMO_KV, "day:" + day, 90000)) > dailyCap) return json({ error: "The demo has reached today's limit. Try again tomorrow, or use the recorded examples." }, 429, cors);

  const callModel = async (system, user) => {
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), 8000);
    try {
      const r = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST", signal: ctl.signal,
        headers: { "content-type": "application/json", "x-api-key": env.ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01" },
        body: JSON.stringify({ model: MODEL, max_tokens: 512, system, messages: [{ role: "user", content: user }] }),
      });
      if (!r.ok) throw new Error("upstream " + r.status);
      const data = await r.json();
      return (data.content || []).map((b) => b.text || "").join("");
    } finally { clearTimeout(timer); }
  };
  try {
    return json(await classify(text, callModel), 200, cors);
  } catch {
    return json({ error: "The model is unavailable right now. The recorded examples still work." }, 502, cors);
  }
}
