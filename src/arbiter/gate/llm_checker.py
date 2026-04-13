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
            "description": "ONLY include terms whose meaning ACTUALLY SHIFTED. Do NOT include terms used consistently.",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "term": {"type": "string"},
                    "shifted": {
                        "type": "boolean",
                        "description": "True ONLY if the term's meaning changed from its seed definition. False if used consistently.",
                    },
                    "description": {"type": "string"},
                    "flagged_explicitly": {"type": "boolean"},
                },
                "required": ["term", "shifted", "description", "flagged_explicitly"],
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
        "1. A turn violates a stipulated fact if it ASSERTS BOTH HALVES of a contradiction simultaneously.",
        "2. CRITICAL: An agent arguing FOR one side of a debate is NOT violating a stipulation.",
        "   - A Proponent saying 'consciousness is computable' is NOT a violation — that's their POSITION.",
        "   - A Skeptic saying 'qualia are irreducible' is NOT a violation — that's their POSITION.",
        "   - A violation is when a SINGLE agent asserts BOTH sides simultaneously, e.g.",
        "     'consciousness is fully computable AND has irreducible non-computable properties'.",
        "3. Paraphrases of genuine violations count — don't require exact wording.",
        "4. A turn that EXPLICITLY ADOPTS a repair path is NOT a violation — BUT check the",
        "   ENTIRE turn. If the agent says 'I adopt repair A' then later says 'that said,",
        "   the original formulation where edges are created remains compelling', the second",
        "   part REASSERTS the violation. Check beyond the opening sentence.",
        "5. 'Two modes' or 'different operational regimes' that assert BOTH halves ARE violations.",
        "6a. QUOTING is NOT asserting. If the agent says 'Torres wrote X and Y' or 'Section N",
        "    states X' or 'the paper claims X', they are REPORTING, not DEFENDING. Look for",
        "    framing: 'wrote', 'claims', 'states', 'argued', 'the paper says'. Quoting both",
        "    halves to CRITICIZE them is NOT a violation.",
        "6. Unflagged shifts of seed terms are violations. BUT with THREE exceptions:",
        "   a) Debating what a term MEANS as part of the topic is NOT a shift.",
        "   b) REPAIRING a stipulated contradiction by explicitly redefining a term",
        "      IS ALLOWED. If an agent says 'Under repair, Royal Purple means X",
        "      instead of Y' or 'I redefine X as...' or 'I drop the edge-creation",
        "      reading of X' — that is a SANCTIONED repair, not a violation.",
        "      Set shifted=false for acknowledged repairs.",
        "   c) If a term is used consistently with its seed definition, set shifted=false.",
        "   ONLY set shifted=true when an agent SILENTLY changes a definition to",
        "   escape a rebuttal — without acknowledging the change.",
        "7. Confidence: high (agent clearly asserts BOTH halves), medium (probable), low (arguable).",
        "8. Only flag HIGH confidence violations. When in doubt, do NOT flag.",
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

        # Check definitional shifts (only flag ACTUAL shifts, not consistent usage)
        for shift in result.get("definitional_shifts", []):
            term = shift.get("term", "").strip()
            if not term:
                continue
            # Skip if the LLM says the term was NOT shifted
            if not shift.get("shifted", True):
                continue
            is_seed = any(
                k.lower() in term.lower() or term.lower() in k.lower()
                for k in self.config.seed_terms
            )
            if is_seed or not shift.get("flagged_explicitly", False):
                violations.append({
                    "type": "llm_definitional_shift",
                    "term": term,
                    "description": shift.get("description", ""),
                    "flagged_explicitly": shift.get("flagged_explicitly", False),
                })

        return violations
