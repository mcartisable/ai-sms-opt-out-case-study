"""Example inbound-message handler showing the four rollout phases. Adapt `Actions` to your own code.

It is framework-agnostic: call handle_inbound() from your Twilio or Infobip webhook after your existing keyword
matcher has run. Webhook specifics (signature checks, response format) belong in your service, not here.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional, Protocol

from .core import Decision, OptOutClassifier, interpret_confirmation_reply
from .shadow import ShadowLogger


class Mode(Enum):
    SHADOW = "shadow"    # log only, change nothing
    REVIEW = "review"    # anything that is not 'no action' goes to the human review queue
    CONFIRM = "confirm"  # would-be opt-outs get the confirmation SMS; uncertain cases go to review
    AUTO = "auto"        # full routing: high-confidence opt-outs happen at once


class Actions(Protocol):
    def opt_out(self, phone: str, reason: str) -> None: ...             # suppress marketing, write the audit record
    def send_confirmation(self, phone: str) -> None: ...                # fixed template: "Reply YES to unsubscribe"
    def enqueue_review(self, message_id: str, phone: str, text: str, decision: Decision) -> None: ...
    def mark_pending_confirmation(self, phone: str) -> None: ...
    def is_pending_confirmation(self, phone: str) -> bool: ...
    def clear_pending_confirmation(self, phone: str) -> None: ...


def handle_inbound(message_id: str, phone: str, text: str, *, keyword_handled: bool, classifier: OptOutClassifier,
                   actions: Actions, mode: Mode, shadow: Optional[ShadowLogger] = None) -> Optional[Decision]:
    """Call for every inbound reply. keyword_handled=True means your existing matcher already opted the person out."""
    if keyword_handled:
        return None  # existing behavior stays authoritative; the classifier never sees these
    if actions.is_pending_confirmation(phone):
        answer = interpret_confirmation_reply(text)
        if answer == "confirm" and mode != Mode.SHADOW:
            actions.opt_out(phone, "confirmed by reply")
            actions.clear_pending_confirmation(phone)
            return None
        if answer == "decline" and mode != Mode.SHADOW:
            actions.clear_pending_confirmation(phone)
            return None
        # anything else falls through and is classified normally

    d = classifier.decide(text)
    if shadow is not None:
        shadow.log(message_id, text, d, existing_system_action="none")
    if mode == Mode.SHADOW:
        return d

    r = d.route
    if r == "no_action":
        return d
    if mode == Mode.REVIEW:
        actions.enqueue_review(message_id, phone, text, d)
    elif mode == Mode.CONFIRM and r in ("auto_opt_out", "send_confirmation"):
        actions.send_confirmation(phone)
        actions.mark_pending_confirmation(phone)
    elif mode == Mode.AUTO and r == "auto_opt_out":
        actions.opt_out(phone, "classifier %s (%.2f)" % (d.label, d.confidence))
    elif mode == Mode.AUTO and r == "send_confirmation":
        actions.send_confirmation(phone)
        actions.mark_pending_confirmation(phone)
    else:  # human_review, or a route this mode does not act on
        actions.enqueue_review(message_id, phone, text, d)
    return d
