"""Export debate state as structured JSON."""

from __future__ import annotations

import json
from typing import Any, Dict


def export_json(state: Dict[str, Any], metadata: Dict[str, Any] | None = None) -> str:
    """Return an indented JSON string of the full debate state.

    Parameters
    ----------
    state:
        Dict matching :class:`arbiter.state.DebateState` keys.
    metadata:
        Optional extra fields (posture, config hash, timestamps, etc.)
        merged into the top-level output.
    """
    payload: Dict[str, Any] = {"state": state}
    if metadata:
        payload["metadata"] = metadata
    return json.dumps(payload, indent=2, default=str, ensure_ascii=False)
