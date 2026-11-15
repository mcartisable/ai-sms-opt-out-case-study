"""Shadow-mode logging: record what the classifier WOULD do, take no action, and measure it later.

One JSON object per line. By default the message text is not stored, only a short hash, so the log carries no personal
data; set store_text=True in a controlled environment when reviewers need to read replies for labeling.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .core import Decision


class ShadowLogger:
    def __init__(self, path: str, store_text: bool = False) -> None:
        self.path, self.store_text = Path(path), store_text
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message_id: str, text: str, decision: Decision, existing_system_action: Optional[str] = None) -> None:
        """existing_system_action: what the current keyword-only system did, e.g. 'opt_out' or 'none'."""
        row: Dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "message_id": message_id,
            "text_sha": hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:12],
            "existing_system_action": existing_system_action, **decision.as_dict()}
        if self.store_text:
            row["text"] = text
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
