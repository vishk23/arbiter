"""Mid-debate per-agent guidance signals."""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING

from arbiter.config import MidDebateConfig

if TYPE_CHECKING:
    from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)

_SYSTEM = (
    "You are a debate referee. Emit STRICT JSON only: "
    '{"agent_name": "one-sentence guidance", ...}. '
    "No prose outside the JSON object."
)


class MidDebateJudge:
    """Generate per-agent guidance signals after each round."""

    def __init__(
        self,
        config: MidDebateConfig,
        provider: "BaseProvider",
    ) -> None:
        self.config = config
        self.provider = provider

    def generate_signals(
        self,
        round_idx: int,
        round_transcript: list[dict],
        open_hits: list[dict],
    ) -> dict[str, str]:
        """Return ``{agent_name: "one-sentence guidance"}`` for the round.

        Parameters
        ----------
        round_idx:
            Zero-based round index that just finished.
        round_transcript:
            List of turn dicts with at least ``agent`` and ``text`` keys.
        open_hits:
            Ledger entries with ``status == "open"``; each has ``id``,
            ``by``, ``against``, ``claim`` keys.
        """
        round_text = "\n\n".join(
            f"[{t['agent']}]\n{t['text'][:1500]}" for t in round_transcript
        )
        hits_text = "\n".join(
            f"  [{h['id']}] {h['by']} -> {h['against']}: {h['claim']}"
            for h in open_hits[:10]
        )

        user_prompt = (
            f"Round {round_idx} just finished. Emit per-agent ONE-SENTENCE "
            f'guidance as JSON: {{"agent_name": "guidance"}}. Focus on the '
            f"SINGLE most important thing each agent should do next.\n\n"
            f"Open hits:\n{hits_text}\n\n"
            f"ROUND TRANSCRIPT:\n{round_text}\n\n"
            "Return JSON only."
        )

        try:
            raw = self.provider.call(
                system=_SYSTEM,
                user=user_prompt,
                max_tokens=1500,
            )
        except Exception:
            logger.exception("Mid-debate judge call failed for round %d", round_idx)
            return {}

        # Parse JSON from response (may be wrapped in markdown fences)
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except (json.JSONDecodeError, ValueError):
                logger.warning("Could not parse mid-debate JSON: %s", raw[:300])
        return {}
