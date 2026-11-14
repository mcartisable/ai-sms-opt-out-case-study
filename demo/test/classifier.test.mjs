import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { isBareKeyword, parseLlmJson, route, classify } from "../functions/_shared/classifier.js";
import { PROMPT_SHA, PROMPT_V3 } from "../functions/_shared/prompt.js";
import { createHash } from "node:crypto";

const fx = JSON.parse(readFileSync(new URL("./fixtures.json", import.meta.url)));

test("prompt text matches the Python prompt v3 hash", () => {
  assert.equal(createHash("sha256").update(PROMPT_V3, "utf8").digest("hex").slice(0, 8), fx.prompt_sha);
  assert.equal(PROMPT_SHA, fx.prompt_sha);
});
test("bare keyword rule matches Python", () => { for (const [t, want] of fx.bare) assert.equal(isBareKeyword(t), want, t); });
test("parser matches Python", () => { for (const [t, want] of fx.parse) assert.deepEqual(parseLlmJson(t), want, JSON.stringify(t)); });
test("routing matches Python", () => { for (const [l, c, want] of fx.route) assert.equal(route(l, c), want, l + " " + c); });
test("keyword shortcut never calls the model", async () => {
  const r = await classify("STOP", async () => { throw new Error("should not be called"); });
  assert.equal(r.route, "auto_opt_out"); assert.equal(r.source, "keyword");
});
test("keyword inside a sentence goes to the model", async () => {
  let called = false;
  const r = await classify("Cancel my order", async () => { called = true; return '{"label":"not_opt_out","confidence":0.95}'; });
  assert.ok(called); assert.equal(r.route, "no_action");
});
test("unparseable model output routes to review", async () => {
  const r = await classify("hello there", async () => "I cannot do that");
  assert.equal(r.route, "human_review"); assert.equal(r.source, "parse_failure");
});
