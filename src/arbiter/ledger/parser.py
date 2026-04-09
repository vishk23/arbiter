"""JSON block extraction from agent output."""

from __future__ import annotations

import json
import logging
import re

logger = logging.getLogger(__name__)


def parse_ledger_block(text: str) -> dict:
    """Extract the `````json ... ``` `` block from an agent's output.

    Returns a dict with keys ``new_hits`` and ``hits_addressed``, each
    a (possibly empty) list.  Resilient to malformed JSON -- returns
    empty containers on any parse failure.
    """
    empty: dict = {"new_hits": [], "hits_addressed": []}

    # Try fenced JSON block first
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            return {
                "new_hits": data.get("new_hits", []),
                "hits_addressed": data.get("hits_addressed", []),
            }
        except (json.JSONDecodeError, ValueError):
            pass

    # Fallback: try any JSON object containing "new_hits" or "hits_addressed"
    for m in re.finditer(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL):
        try:
            data = json.loads(m.group(0))
            if "new_hits" in data or "hits_addressed" in data:
                return {
                    "new_hits": data.get("new_hits", []),
                    "hits_addressed": data.get("hits_addressed", []),
                }
        except (json.JSONDecodeError, ValueError):
            continue

    logger.debug("No ledger block found in agent output (%d chars)", len(text))
    return empty
