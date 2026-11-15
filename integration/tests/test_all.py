from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from optout_classifier import OptOutClassifier, PROMPT_SHA, interpret_confirmation_reply, is_bare_keyword, route  # noqa: E402
from optout_classifier.handler import Mode, handle_inbound  # noqa: E402
from optout_classifier.shadow import ShadowLogger  # noqa: E402

FX = json.loads((HERE.parent.parent / "demo/test/fixtures.json").read_text())


class FakeClient:
    """Stands in for the Anthropic client. `reply` is text, or an Exception to raise."""

    def __init__(self, reply):
        self.reply, self.calls = reply, 0
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kw):
        self.calls += 1
        if isinstance(self.reply, Exception):
            raise self.reply
        return SimpleNamespace(content=[SimpleNamespace(text=self.reply)])


def model(label, conf):
    return FakeClient(json.dumps({"label": label, "confidence": conf}))


class Parity(unittest.TestCase):
    def test_prompt_hash_matches_prototype(self):
        self.assertEqual(PROMPT_SHA, FX["prompt_sha"])

    def test_bare_keyword_matches_prototype_for_english(self):
        for text, want in FX["bare"]:
            if text in ("СТОП", "baja"):
                continue  # the package is English only
            self.assertEqual(is_bare_keyword(text), want, text)

    def test_routing_matches_prototype(self):
        for label, conf, want in FX["route"]:
            self.assertEqual(route(label, conf), want, (label, conf))


class Decide(unittest.TestCase):
    def test_keyword_never_calls_model(self):
        c = FakeClient("x")
        d = OptOutClassifier(client=c).decide("STOP")
        self.assertEqual((d.route, d.source, c.calls), ("auto_opt_out", "keyword", 0))

    def test_model_routes(self):
        for label, conf, want in [("opt_out", 0.95, "auto_opt_out"), ("opt_out", 0.7, "send_confirmation"),
                                  ("opt_out", 0.4, "human_review"), ("ambiguous", 0.9, "human_review"), ("not_opt_out", 0.9, "no_action")]:
            d = OptOutClassifier(client=model(label, conf)).decide("some reply")
            self.assertEqual(d.route, want)
            self.assertEqual(d.source, "model")
            self.assertEqual(d.prompt_sha, PROMPT_SHA)

    def test_errors_route_to_review_and_never_raise(self):
        d = OptOutClassifier(client=FakeClient(TimeoutError("slow"))).decide("please stop texting me")
        self.assertEqual((d.route, d.source, d.error), ("human_review", "error", "TimeoutError"))

    def test_unparseable_output_routes_to_review(self):
        d = OptOutClassifier(client=FakeClient("I cannot help with that")).decide("hello")
        self.assertEqual((d.route, d.source), ("human_review", "parse_failure"))

    def test_empty_and_too_long(self):
        c = FakeClient("x")
        k = OptOutClassifier(client=c, max_chars=50)
        self.assertEqual(k.decide("   ").route, "no_action")
        self.assertEqual(k.decide("word " * 30).route, "human_review")
        self.assertEqual(c.calls, 0)

    def test_keyword_inside_a_sentence_goes_to_model(self):
        c = model("not_opt_out", 0.95)
        d = OptOutClassifier(client=c).decide("Cancel my order")
        self.assertEqual((d.route, c.calls), ("no_action", 1))

    def test_confirmation_replies(self):
        self.assertEqual(interpret_confirmation_reply("YES"), "confirm")
        self.assertEqual(interpret_confirmation_reply("yes please!"), "confirm")
        self.assertEqual(interpret_confirmation_reply("No thanks"), "decline")
        self.assertEqual(interpret_confirmation_reply("where is my order"), "other")


class FakeActions:
    def __init__(self):
        self.log, self.pending = [], set()

    def opt_out(self, phone, reason): self.log.append(("opt_out", phone))
    def send_confirmation(self, phone): self.log.append(("confirm", phone))
    def enqueue_review(self, mid, phone, text, d): self.log.append(("review", phone))
    def mark_pending_confirmation(self, phone): self.pending.add(phone)
    def is_pending_confirmation(self, phone): return phone in self.pending
    def clear_pending_confirmation(self, phone): self.pending.discard(phone)


def run(mode, label, conf, text="reply", phone="+1555", actions=None, **kw):
    a = actions or FakeActions()
    handle_inbound("m1", phone, text, keyword_handled=kw.pop("keyword_handled", False),
                   classifier=OptOutClassifier(client=model(label, conf)), actions=a, mode=mode, **kw)
    return a


class Handler(unittest.TestCase):
    def test_shadow_takes_no_action(self):
        for label, conf in [("opt_out", 0.99), ("ambiguous", 0.5), ("not_opt_out", 0.9)]:
            self.assertEqual(run(Mode.SHADOW, label, conf).log, [])

    def test_review_mode_queues_everything_actionable(self):
        self.assertEqual(run(Mode.REVIEW, "opt_out", 0.99).log, [("review", "+1555")])
        self.assertEqual(run(Mode.REVIEW, "not_opt_out", 0.9).log, [])

    def test_confirm_mode(self):
        self.assertEqual(run(Mode.CONFIRM, "opt_out", 0.99).log, [("confirm", "+1555")])
        self.assertEqual(run(Mode.CONFIRM, "ambiguous", 0.7).log, [("review", "+1555")])

    def test_auto_mode(self):
        self.assertEqual(run(Mode.AUTO, "opt_out", 0.95).log, [("opt_out", "+1555")])
        self.assertEqual(run(Mode.AUTO, "opt_out", 0.7).log, [("confirm", "+1555")])
        self.assertEqual(run(Mode.AUTO, "opt_out", 0.3).log, [("review", "+1555")])

    def test_keyword_handled_is_not_classified(self):
        self.assertEqual(run(Mode.AUTO, "opt_out", 0.99, keyword_handled=True).log, [])

    def test_confirmation_flow(self):
        a = run(Mode.AUTO, "opt_out", 0.7)
        self.assertIn("+1555", a.pending)
        run(Mode.AUTO, "not_opt_out", 0.9, text="YES", actions=a)
        self.assertEqual(a.log[-1], ("opt_out", "+1555"))
        self.assertNotIn("+1555", a.pending)
        b = run(Mode.AUTO, "opt_out", 0.7)
        run(Mode.AUTO, "not_opt_out", 0.9, text="no", actions=b)
        self.assertEqual([x[0] for x in b.log], ["confirm"])

    def test_errors_become_review_in_every_acting_mode(self):
        for mode in (Mode.REVIEW, Mode.CONFIRM, Mode.AUTO):
            a = FakeActions()
            handle_inbound("m", "+1", "please stop texting me", keyword_handled=False,
                           classifier=OptOutClassifier(client=FakeClient(ConnectionError())), actions=a, mode=mode)
            self.assertEqual(a.log, [("review", "+1")])


class Shadow(unittest.TestCase):
    def test_log_stores_hash_not_text_and_report_scores(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "s.jsonl"
            sh = ShadowLogger(str(log))
            items = [("m1", "please stop texting me", "opt_out", model("opt_out", 0.95)), ("m2", "where is my order", "not_opt_out", model("not_opt_out", 0.9)),
                     ("m3", "enough already", "opt_out", model("ambiguous", 0.6))]
            for mid, text, _, cl in items:
                sh.log(mid, text, OptOutClassifier(client=cl).decide(text), existing_system_action="none")
            self.assertNotIn("please stop", log.read_text())
            labels = Path(d) / "l.csv"
            with labels.open("w", newline="") as f:
                w = csv.writer(f); w.writerow(["message_id", "label"]); [w.writerow([m, l]) for m, _, l, _ in items]
            out = subprocess.run([sys.executable, str(HERE.parent / "shadow_report.py"), str(log), "--labels", str(labels)],
                                 capture_output=True, text=True, check=True).stdout
            self.assertIn("recall as label: 1/2", out)
            self.assertIn("non-opt-outs it would opt out automatically: 0", out)


if __name__ == "__main__":
    unittest.main()
