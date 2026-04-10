"""LLM-based primary validity checker.

Replaces regex as the primary gate check. Uses a cheap model (nano/mini)
to classify whether a debate turn violates any stipulated fact.

Advantages over regex:
- Catches paraphrases (regex can't)
- No brittle pattern generation needed
- Works on auto-generated configs without hand-tuning
- Cost: ~$0.004 per check with gpt-5.4-nano (negligible)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arbiter.config import GateConfig
    from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)

VIOLATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "violations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "rule_id": {
                        "type": "string",
                        "description": "ID of the stipulated rule violated.",
                    },
                    "violated": {
                        "type": "boolean",
                        "description": "True if this rule is violated.",
                    },
                    "explanation": {
                        "type": "string",
                        "description": "One sentence explaining how the turn violates this rule.",
                    },
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                    },
                },
                "required": ["rule_id", "violated", "explanation", "confidence"],
            },
        },
        "definitional_shifts": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "term": {"type": "string"},
                    "description": {"type": "string"},
                    "flagged_explicitly": {"type": "boolean"},
                },
                "required": ["term", "description", "flagged_explicitly"],
            },
        },
    },
    "required": ["violations", "definitional_shifts"],
}


def _build_system_prompt(config: "GateConfig") -> str:
    """Build the LLM checker system prompt from stipulated rules + seed terms."""
    parts = [
        "You are a STRICT validity checker for a structured debate.",
        "Check whether the debate turn below violates ANY of the stipulated facts.",
        "",
        "STIPULATED FACTS (proven, non-negotiable):",
    ]

    for rule in config.stipulated_rules:
        parts.append(f"  [{rule.id}] {rule.fact}")

    if not config.stipulated_rules:
        parts.append("  (no explicit rules — check for internal self-contradiction only)")

    if config.seed_terms:
        parts.append("")
        parts.append("SEED TERMS (canonical definitions — any shift is a violation):")
        for term, defn in config.seed_terms.items():
            parts.append(f"  {term}: {defn}")

    parts.extend([
        "",
        "RULES:",
        "1. A turn violates a stipulated fact if it ASSERTS, IMPLIES, or PRESUPPOSES the opposite.",
        "2. Paraphrases count — don't require exact wording.",
        "3. A turn that EXPLICITLY ADOPTS a repair path (e.g. 'I drop claim X' or 'Under repair A, X is not Y') is NOT a violation.",
        "4. 'Two modes' or 'different operational regimes' framings that assert BOTH halves ARE violations.",
        "5. Any unflagged shift of a seed term (using it with a different meaning without explicit notice) is a violation.",
        "6. Flag confidence: high (clear violation), medium (likely violation), low (ambiguous).",
        "7. Only flag medium and high confidence violations.",
        "",
        "Return STRICT JSON. For each rule, report whether it's violated.",
    ])

    return "\n".join(parts)


class LLMChecker:
    """Primary LLM-based validity checker.

    Uses a cheap model (nano/mini) to classify violations. Replaces regex
    as the primary check; regex can be kept as optional additive.
    """

    def __init__(self, config: "GateConfig", provider: "BaseProvider") -> None:
        self.config = config
        self.provider = provider
        self._system = _build_system_prompt(config)

    def check(self, turn_text: str) -> list[dict]:
        """Check *turn_text* against all stipulated facts.

        Returns a list of violation dicts (medium/high confidence only).
        Fails open on errors (returns empty list).
        """
        user = f"DEBATE TURN TO CHECK:\n\n{turn_text}"

        try:
            result = self.provider.call_structured(
                system=self._system,
                user=user,
                schema=VIOLATION_SCHEMA,
                max_tokens=4000,
            )
        except Exception as exc:
            logger.warning("LLM checker failed (fail-open): %s", exc)
            return []

        violations: list[dict] = []

        # Check rule violations
        for v in result.get("violations", []):
            if not v.get("violated"):
                continue
            if v.get("confidence") == "low":
                continue
            violations.append({
                "type": "llm_violation",
                "rule_id": v.get("rule_id", "?"),
                "reason": v.get("explanation", ""),
                "confidence": v.get("confidence", "medium"),
            })

        # Check definitional shifts
        for shift in result.get("definitional_shifts", []):
            term = shift.get("term", "").lower()
            is_seed = any(
                k.lower() in term or term in k.lower()
                for k in self.config.seed_terms
            )
            if is_seed or not shift.get("flagged_explicitly", False):
                violations.append({
                    "type": "llm_definitional_shift",
                    "term": shift.get("term", ""),
                    "description": shift.get("description", ""),
                    "flagged_explicitly": shift.get("flagged_explicitly", False),
                })

        return violations
