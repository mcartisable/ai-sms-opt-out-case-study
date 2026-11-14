import test from "node:test";
import assert from "node:assert/strict";
import { onRequest } from "../functions/api/classify.js";

const kv = () => { const m = new Map(); return { get: async (k) => m.get(k) ?? null, put: async (k, v) => { m.set(k, v); } }; };
const req = (body, headers = {}, method = "POST") => new Request("https://demo.example/api/classify", {
  method, headers: { "content-type": "application/json", "cf-connecting-ip": "1.2.3.4", ...headers },
  body: method === "POST" ? (typeof body === "string" ? body : JSON.stringify(body)) : undefined });
const env = (extra = {}) => ({ ANTHROPIC_API_KEY: "test-key", DEMO_KV: kv(), ...extra });
const fakeModel = (label, confidence) => { globalThis.fetch = async () => new Response(JSON.stringify({ content: [{ type: "text", text: JSON.stringify({ label, confidence }) }] })); };

test("503 when key or KV is missing", async () => {
  const r = await onRequest({ request: req({ text: "hi" }), env: { DEMO_KV: kv() } });
  assert.equal(r.status, 503);
});
test("validates input", async () => {
  assert.equal((await onRequest({ request: req({ text: "" }), env: env() })).status, 400);
  assert.equal((await onRequest({ request: req("not json"), env: env() })).status, 400);
  assert.equal((await onRequest({ request: req({ text: "x".repeat(301) }), env: env() })).status, 413);
  assert.equal((await onRequest({ request: req({ text: "hi" }, {}, "GET"), env: env() })).status, 405);
});
test("blocks other origins, allows same origin and listed origins", async () => {
  fakeModel("not_opt_out", 0.9);
  assert.equal((await onRequest({ request: req({ text: "hi" }, { origin: "https://evil.example" }), env: env() })).status, 403);
  assert.equal((await onRequest({ request: req({ text: "hi" }, { origin: "https://demo.example" }), env: env() })).status, 200);
  const r = await onRequest({ request: req({ text: "hi" }, { origin: "https://me.example" }), env: env({ ALLOWED_ORIGINS: "https://me.example" }) });
  assert.equal(r.status, 200); assert.equal(r.headers.get("access-control-allow-origin"), "https://me.example");
});
test("classifies through the model and routes", async () => {
  fakeModel("opt_out", 0.95);
  const r = await onRequest({ request: req({ text: "please stop texting me" }), env: env() });
  assert.deepEqual(await r.json(), { label: "opt_out", confidence: 0.95, source: "model", route: "auto_opt_out" });
});
test("keyword shortcut works without calling the model", async () => {
  globalThis.fetch = async () => { throw new Error("no model call expected"); };
  const r = await onRequest({ request: req({ text: "STOP" }), env: env() });
  assert.equal((await r.json()).source, "keyword");
});
test("per-IP hourly limit", async () => {
  fakeModel("not_opt_out", 0.9);
  const e = env({ HOURLY_PER_IP: "2" });
  assert.equal((await onRequest({ request: req({ text: "a" }), env: e })).status, 200);
  assert.equal((await onRequest({ request: req({ text: "b" }), env: e })).status, 200);
  assert.equal((await onRequest({ request: req({ text: "c" }), env: e })).status, 429);
});
test("global daily cap", async () => {
  fakeModel("not_opt_out", 0.9);
  const e = env({ DAILY_CAP: "1" });
  assert.equal((await onRequest({ request: req({ text: "a" }, { "cf-connecting-ip": "9.9.9.1" }), env: e })).status, 200);
  assert.equal((await onRequest({ request: req({ text: "b" }, { "cf-connecting-ip": "9.9.9.2" }), env: e })).status, 429);
});
test("upstream failure returns 502 without leaking details", async () => {
  globalThis.fetch = async () => new Response("secret upstream body", { status: 500 });
  const r = await onRequest({ request: req({ text: "hello" }), env: env() });
  assert.equal(r.status, 502); assert.ok(!(await r.text()).includes("secret"));
});
