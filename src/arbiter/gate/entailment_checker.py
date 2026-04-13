"""LLM semantic backstop for stipulation violations via entailment checking."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from arbiter.config import EntailmentCheckConfig, TokenBudgets
from arbiter.schemas import EntailmentResult

_B = TokenBudgets()

if TYPE_CHECKING:
    from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)

# Backward-compat: dict form of the schema for external consumers.
ENTAILMENT_SCHEMA = EntailmentResult.model_json_schema()


class EntailmentChecker:
    """Semantic backstop: asks an LLM whether a turn entails any stipulation
    violation.  Catches paraphrases that the regex engine misses.

    The system prompt comes from ``config.system_prompt``.  If not provided
    the checker is effectively a no-op (returns no violations).

    **Fail-open**: any error during the LLM call is logged and an empty list
    is returned so the gate does not block on transient provider failures.
    """

    def __init__(self, config: EntailmentCheckConfig, provider: "BaseProvider") -> None:
        self.config = config
        self.provider = provider

    def check(self, turn_text: str) -> list[dict]:
        """Return entailment-violation dicts (medium/high confidence only)."""
        if not self.config.enabled:
            return []
        system = self.config.system_prompt or ""
        if not system:
            return []

        user = (
            f"TURN TEXT:\n{turn_text}\n\n"
            "Does this turn entail any stipulated-fact violation?"
        )
        try:
            result = self.provider.call_structured(
                system=system,
                user=user,
                schema=EntailmentResult,
                max_tokens=_B.medium,
            )
        except Exception as exc:
            logger.warning("Entailment check failed (fail-open): %s", exc)
            return []

        if not result.get("violates"):
            return []
        # Only flag medium/high confidence to reduce noise.
        if result.get("confidence") == "low":
            return []

        return [{
            "type": "entailment_violation",
            "rule_id": ",".join(result["violates"]),
            "reason": result["reason"],
            "confidence": result["confidence"],
        }]
