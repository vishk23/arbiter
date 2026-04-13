"""Validity gate orchestrator with rewrite loop.

Two modes (set via ``config.primary``):

- **"llm"** (default): LLM classifier is the primary check. Catches
  paraphrases, definitional shifts, and stipulation violations using a
  cheap model (nano/mini). Regex rules are additive if provided.
  Cost: ~$0.004/turn.

- **"regex"**: Regex patterns are the primary check (deterministic,
  auditable). LLM entailment is a backstop for paraphrases. This is
  the legacy v0.1 behavior for hand-tuned configs.

Z3 structural check runs in both modes (when claims are extractable).
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, Callable

from arbiter.config import GateConfig
from arbiter.gate.consistency_checker import ConsistencyChecker
from arbiter.gate.llm_checker import LLMChecker
from arbiter.gate.pattern_checker import PatternChecker
from arbiter.gate.shift_checker import ShiftChecker
from arbiter.gate.z3_checker import Z3Checker
from arbiter.schemas import ClaimExtractionResult

if TYPE_CHECKING:
    from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)



def _build_extractor_system(seed_terms: dict[str, str]) -> str:
    """Build the claim-extractor system prompt, parameterised by *seed_terms*."""
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
        "  (b) makes a logical / mathematical assertion\n"
        "  (c) makes a definitional statement about a key term\n\n"
        "DEFINITIONAL SHIFTS -- a term being used with a meaning that differs from prior definitions.\n"
        "Flag even when the speaker names the shift -- set flagged_explicitly=true only when the "
        "speaker EXPLICITLY says 'I am switching definitions'.\n\n"
        "Return STRICT JSON only."
    )


def extract_formal_claims(
    provider: "BaseProvider",
    text: str,
    known_terms: dict[str, str],
    seed_terms: dict[str, str] | None = None,
) -> dict:
    """Use *provider* to extract formal claims and definitional shifts."""
    prior_ctx = (
        "\n".join(f"  {t}: {d}" for t, d in known_terms.items()) or "  (none yet)"
    )
    user = (
        f"PRIOR TERM DEFINITIONS:\n{prior_ctx}\n\n"
        f"TURN TEXT:\n{text}\n\n"
        f"Extract formal_claims and definitional_shifts as JSON."
    )
    system = _build_extractor_system(seed_terms or {})
    try:
        return provider.call_structured(
            system=system, user=user, schema=ClaimExtractionResult, max_tokens=6000,
        )
    except Exception as exc:
        logger.warning("Claim extraction failed (fail-open): %s", exc)
        return {"formal_claims": [], "definitional_shifts": [], "_extractor_error": str(exc)}


# ── Orchestrator ──────────────────────────────────────────────────────


class ValidityGate:
    """Run the full validity pipeline on a single debate turn.

    When ``primary="llm"`` (default):
      1. LLM classifier (catches violations + shifts in one call)
      2. Regex patterns (additive, only if stipulated_rules exist)
      3. Z3 structural check (only if structural claims extractable)

    When ``primary="regex"`` (legacy):
      1. Claim extraction (LLM)
      2. Regex patterns
      3. Self-consistency
      4. Shift checker
      5. Z3 structural check
      6. LLM entailment backstop
    """

    def __init__(
        self,
        config: GateConfig,
        providers: dict[str, "BaseProvider"],
    ) -> None:
        self.config = config
        self.providers = providers
        self._mode = config.primary  # "llm" or "regex"

        # Resolve extraction provider
        self._extraction_provider: BaseProvider | None = None
        if config.extraction_provider and config.extraction_provider in providers:
            self._extraction_provider = providers[config.extraction_provider]
        elif providers:
            self._extraction_provider = next(iter(providers.values()))

        # LLM primary checker (for mode="llm")
        self._llm_checker: LLMChecker | None = None
        if self._mode == "llm" and self._extraction_provider:
            # Use dedicated provider/model if specified, else extraction provider
            llm_provider = self._extraction_provider
            if config.llm_checker_provider and config.llm_checker_provider in providers:
                llm_provider = providers[config.llm_checker_provider]
            self._llm_checker = LLMChecker(config, llm_provider)

        # Regex pattern checker (additive in llm mode, primary in regex mode)
        self._pattern = PatternChecker(config.stipulated_rules)

        # Legacy checkers (only used in regex mode)
        self._consistency = ConsistencyChecker()
        self._shift = ShiftChecker(config.seed_terms)
        self._z3 = Z3Checker()

        # Legacy entailment backstop (only used in regex mode)
        from arbiter.gate.entailment_checker import EntailmentChecker
        self._entailment: EntailmentChecker | None = None
        if self._mode == "regex" and config.entailment_check and config.entailment_check.enabled:
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
        """Run the validity pipeline. Returns ``{passed, violations, extracted}``."""
        if self._mode == "llm":
            return self._check_llm_primary(agent, turn_text, prior_claims, known_terms)
        else:
            return self._check_regex_primary(agent, turn_text, prior_claims, known_terms)

    def _check_llm_primary(
        self, agent: str, turn_text: str,
        prior_claims: dict[str, list[dict]], known_terms: dict[str, str],
    ) -> dict[str, Any]:
        """LLM-primary mode: one LLM call catches everything."""
        violations: list[dict] = []
        extracted: dict = {"formal_claims": [], "definitional_shifts": []}

        # (1) LLM classifier — primary check
        if self._llm_checker:
            violations += self._llm_checker.check(turn_text)

        # (2) Regex patterns — additive (catches what LLM might miss)
        if self.config.stipulated_rules:
            violations += self._pattern.check(turn_text)

        # (3) Z3 structural check — extract claims first if provider available
        if self._extraction_provider:
            extracted = extract_formal_claims(
                self._extraction_provider, turn_text, known_terms,
                seed_terms=self.config.seed_terms,
            )
            structural = [
                c["claim"] for c in extracted.get("formal_claims", [])
                if c.get("category") == "structural"
            ]
            z3res = self._z3.check(structural)
            if z3res:
                violations.append(z3res)

        # Deduplicate (LLM + regex might both catch the same violation)
        seen_rules: set[str] = set()
        unique: list[dict] = []
        for v in violations:
            rule_id = v.get("rule_id", "")
            if rule_id and rule_id in seen_rules:
                continue
            if rule_id:
                seen_rules.add(rule_id)
            unique.append(v)

        return {"passed": len(unique) == 0, "violations": unique, "extracted": extracted}

    def _check_regex_primary(
        self, agent: str, turn_text: str,
        prior_claims: dict[str, list[dict]], known_terms: dict[str, str],
    ) -> dict[str, Any]:
        """Legacy regex-primary mode (v0.1 behavior)."""
        if self._extraction_provider:
            extracted = extract_formal_claims(
                self._extraction_provider, turn_text, known_terms,
                seed_terms=self.config.seed_terms,
            )
        else:
            extracted = {"formal_claims": [], "definitional_shifts": []}

        violations: list[dict] = []
        violations += self._pattern.check(turn_text)
        violations += self._consistency.check(
            agent, extracted.get("formal_claims", []), prior_claims,
        )
        violations += self._shift.check(extracted.get("definitional_shifts", []))

        structural = [
            c["claim"] for c in extracted.get("formal_claims", [])
            if c.get("category") == "structural"
        ]
        z3res = self._z3.check(structural)
        if z3res:
            violations.append(z3res)

        if (
            self._entailment
            and not any(v.get("type") == "stipulation_violation" for v in violations)
        ):
            violations += self._entailment.check(turn_text)

        return {"passed": len(violations) == 0, "violations": violations, "extracted": extracted}

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
        """Produce a turn, gating it with up to ``max_rewrites`` attempts."""
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
            if attempt_idx < max_rewrites:
                current_user = user + "\n\n" + self.format_rejection(gate["violations"])

        return {
            "entry": result_text,
            "log": attempts,
            "extracted": gate.get("extracted", {}),
        }

    @staticmethod
    def format_rejection(violations: list[dict]) -> str:
        """Format rejection notice for agent rewrite prompt."""
        lines = [
            "REJECTION NOTICE — your previous turn failed the validity gate.",
            "Specific failures:",
        ]
        for i, v in enumerate(violations, 1):
            vtype = v.get("type", "?")
            detail = v.get("reason") or v.get("fact") or v.get("description") or json.dumps(
                {k: v[k] for k in v if k != "type"}, default=str
            )[:300]
            lines.append(f"  ({i}) [{vtype}] {detail}")
        lines.append("")
        lines.append(
            "REWRITE your turn addressing EACH failure. Do not re-assert any "
            "stipulation-violating claim. If you intend a definitional shift, "
            "flag it explicitly."
        )
        return "\n".join(lines)
