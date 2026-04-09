"""Validity gate orchestrator with rewrite loop."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, Callable

from arbiter.config import GateConfig
from arbiter.gate.consistency_checker import ConsistencyChecker
from arbiter.gate.entailment_checker import EntailmentChecker
from arbiter.gate.pattern_checker import PatternChecker
from arbiter.gate.shift_checker import ShiftChecker
from arbiter.gate.z3_checker import Z3Checker

if TYPE_CHECKING:
    from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)

# ── Claim-extraction schema (structural, not topic-specific) ─────────

CLAIM_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "formal_claims": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "claim": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": [
                            "structural",
                            "logical",
                            "definitional",
                            "computability",
                            "other",
                        ],
                    },
                },
                "required": ["claim", "category"],
            },
        },
        "definitional_shifts": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "term": {"type": "string"},
                    "prior_definition": {"type": "string"},
                    "new_definition": {"type": "string"},
                    "flagged_explicitly": {"type": "boolean"},
                },
                "required": [
                    "term",
                    "prior_definition",
                    "new_definition",
                    "flagged_explicitly",
                ],
            },
        },
    },
    "required": ["formal_claims", "definitional_shifts"],
}


def _build_extractor_system(seed_terms: dict[str, str]) -> str:
    """Build the claim-extractor system prompt, parameterised by *seed_terms*.

    The seed-terms list is injected so the extractor knows which terms are
    load-bearing and should be watched for definitional shifts.
    """
    if seed_terms:
        term_lines = "\n".join(f"  - {name}: {defn}" for name, defn in seed_terms.items())
        seed_block = (
            f"SEED TERMS (load-bearing, shifts on these are always flagged):\n{term_lines}\n\n"
        )
    else:
        seed_block = ""

    return (
        "You extract FORMAL CLAIMS and DEFINITIONAL SHIFTS from a debate turn.\n\n"
        + seed_block
        + "FORMAL CLAIMS -- extract ANY statement that:\n"
        "  (a) references a specific structure (e.g. graphs, vertices, edges, functions, states)\n"
        "  (b) makes a logical / mathematical assertion (X implies Y, X is consistent with Y,\n"
        "      X is fixed, X is mutable, X is computable, X holds, X is sound)\n"
        "  (c) makes a definitional statement about a key term\n\n"
        "DEFINITIONAL SHIFTS -- a term is being used with a meaning that differs from PRIOR TERM\n"
        "DEFINITIONS. Be aggressive -- flag ANY of these patterns as definitional shifts (and judge\n"
        "whether they were explicitly flagged by the speaker as a shift):\n\n"
        "EXAMPLES OF DEFINITIONAL SHIFTS YOU MUST FLAG:\n"
        "  - 'When I refer to X, I mean the metatheoretic X' -> SHIFT of X\n"
        "    (flagged_explicitly=true ONLY if the speaker says 'I am switching definitions'\n"
        "     or similar; just naming the shift is NOT enough)\n"
        "  - 'X, properly understood, is ...' -> SHIFT of X\n"
        "  - 'X is best understood as Y, not Z' -> SHIFT of X\n"
        "  - 'The DAG here means the developmental DAG, not the causal DAG' -> SHIFT of DAG\n"
        "  - 'Distinct from X as defined in Section N' -> SHIFT of X\n"
        "  - 'In a richer sense, X is...' -> SHIFT of X\n"
        "  - Any phrase like 'properly understood', 'in the deeper sense', 'really means',\n"
        "    'should be read as', 'distinct from how X was defined' applied to a key term --\n"
        "    these are SHIFTS.\n\n"
        "FLAGGED EXPLICITLY = TRUE only if the speaker EXPLICITLY tells the reader 'I am now\n"
        "using this term differently from before' or 'this is a different sense of the term'.\n"
        "Merely RENAMING without acknowledgment that this is a deviation from prior usage =\n"
        "flagged_explicitly: FALSE.\n\n"
        "Return STRICT JSON only. No prose."
    )


def extract_formal_claims(
    provider: "BaseProvider",
    text: str,
    known_terms: dict[str, str],
    seed_terms: dict[str, str] | None = None,
) -> dict:
    """Use *provider* to extract formal claims and definitional shifts.

    Returns a dict matching :data:`CLAIM_SCHEMA`.  Fails-open (returns
    empty containers) on any provider error.
    """
    prior_ctx = (
        "\n".join(f"  {t}: {d}" for t, d in known_terms.items()) or "  (none yet)"
    )
    user = (
        f"PRIOR TERM DEFINITIONS (from earlier in debate / stipulation):\n{prior_ctx}\n\n"
        f"TURN TEXT:\n{text}\n\n"
        f"Extract formal_claims and definitional_shifts as JSON."
    )
    system = _build_extractor_system(seed_terms or {})
    try:
        return provider.call_structured(
            system=system,
            user=user,
            schema=CLAIM_SCHEMA,
            max_tokens=6000,
        )
    except Exception as exc:
        logger.warning("Claim extraction failed (fail-open): %s", exc)
        return {
            "formal_claims": [],
            "definitional_shifts": [],
            "_extractor_error": str(exc),
        }


# ── Orchestrator ──────────────────────────────────────────────────────


class ValidityGate:
    """Run the full validity pipeline on a single debate turn.

    Pipeline order:
    1. ``extract_formal_claims`` (LLM)
    2. ``PatternChecker`` -- regex stipulation rules
    3. ``ConsistencyChecker`` -- self-contradiction
    4. ``ShiftChecker`` -- definitional shifts
    5. ``Z3Checker`` -- structural SAT (optional)
    6. ``EntailmentChecker`` -- LLM semantic backstop (skipped when a
       stipulation hit already fired, or when not configured)
    """

    def __init__(
        self,
        config: GateConfig,
        providers: dict[str, "BaseProvider"],
    ) -> None:
        self.config = config
        self.providers = providers

        self._pattern = PatternChecker(config.stipulated_rules)
        self._consistency = ConsistencyChecker()
        self._shift = ShiftChecker(config.seed_terms)
        self._z3 = Z3Checker()

        # Resolve extraction provider (explicit, or first available).
        self._extraction_provider: BaseProvider | None = None
        if config.extraction_provider and config.extraction_provider in providers:
            self._extraction_provider = providers[config.extraction_provider]
        elif providers:
            self._extraction_provider = next(iter(providers.values()))

        # Entailment checker (optional).
        self._entailment: EntailmentChecker | None = None
        if config.entailment_check and config.entailment_check.enabled:
            ec = config.entailment_check
            ep = providers.get(ec.provider)
            if ep:
                self._entailment = EntailmentChecker(ec, ep)

    # ── single-turn check ─────────────────────────────────────────────

    def check(
        self,
        agent: str,
        turn_text: str,
        prior_claims: dict[str, list[dict]],
        known_terms: dict[str, str],
    ) -> dict[str, Any]:
        """Run the full validity pipeline.

        Returns ``{passed: bool, violations: list, extracted: dict}``.
        """
        # (0) extract formal claims
        if self._extraction_provider:
            extracted = extract_formal_claims(
                self._extraction_provider,
                turn_text,
                known_terms,
                seed_terms=self.config.seed_terms,
            )
        else:
            extracted = {"formal_claims": [], "definitional_shifts": []}

        violations: list[dict] = []

        # (1) stipulation pattern check
        violations += self._pattern.check(turn_text)

        # (2) self-consistency
        violations += self._consistency.check(
            agent,
            extracted.get("formal_claims", []),
            prior_claims,
        )

        # (3) definitional shifts
        violations += self._shift.check(extracted.get("definitional_shifts", []))

        # (4) Z3 structural SAT
        structural = [
            c["claim"]
            for c in extracted.get("formal_claims", [])
            if c.get("category") == "structural"
        ]
        z3res = self._z3.check(structural)
        if z3res:
            violations.append(z3res)

        # (5) LLM entailment backstop (skip when regex already fired)
        if (
            self._entailment
            and not any(v.get("type") == "stipulation_violation" for v in violations)
        ):
            violations += self._entailment.check(turn_text)

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "extracted": extracted,
        }

    # ── rewrite loop ──────────────────────────────────────────────────

    def run_with_rewrites(
        self,
        call_fn: Callable[[str, str], str],
        agent: str,
        system: str,
        user: str,
        prior_claims: dict[str, list[dict]],
        known_terms: dict[str, str],
    ) -> dict[str, Any]:
        """Produce a turn, gating it with up to ``max_rewrites`` attempts.

        *call_fn(system, user) -> str* invokes the agent's LLM.

        Returns::

            {
                "entry": <final turn text>,
                "log": [<attempt dicts>],
                "extracted": <claims from final attempt>,
            }
        """
        max_rewrites = self.config.max_rewrites
        attempts: list[dict[str, Any]] = []
        current_user = user
        result_text = ""
        gate: dict[str, Any] = {"passed": False, "violations": [], "extracted": {}}

        for attempt_idx in range(max_rewrites + 1):
            result_text = call_fn(system, current_user)
            gate = self.check(agent, result_text, prior_claims, known_terms)
            attempts.append({
                "attempt": attempt_idx,
                "passed": gate["passed"],
                "violations": gate["violations"],
            })
            if gate["passed"]:
                break
            # Prepare rewrite prompt for next iteration.
            if attempt_idx < max_rewrites:
                current_user = (
                    user
                    + "\n\n---\nYOUR PREVIOUS DRAFT (REJECTED):\n"
                    + result_text
                    + "\n\n"
                    + self.format_rejection(gate["violations"])
                )

        return {
            "entry": result_text,
            "log": attempts,
            "extracted": gate.get("extracted", {}),
        }

    # ── rejection formatting ──────────────────────────────────────────

    @staticmethod
    def format_rejection(violations: list[dict]) -> str:
        """Human-readable rejection notice appended to rewrite prompts."""
        lines = [
            "REJECTION NOTICE -- your previous turn failed the VALIDITY GATE.",
            "Specific failures:",
        ]
        for i, v in enumerate(violations, 1):
            detail = json.dumps({k: v[k] for k in v if k != "type"})[:400]
            lines.append(f"  ({i}) [{v.get('type')}] {detail}")
        lines.append("")
        lines.append(
            "REWRITE your turn addressing EACH failure above. Do not "
            "re-assert any stipulation-violating claim. If you intend "
            "a definitional shift, flag it explicitly (e.g., 'I am now "
            "using X in a different sense, distinct from X as "
            "defined above'). Preserve the JSON ledger block at the end."
        )
        return "\n".join(lines)
