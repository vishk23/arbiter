"""Gold-standard calibration of the LLM-primary validity gate.

Same test cases as the original regex gate calibration (test_validity_gate.py
in debate-repos), adapted for the new LLM checker. Measures recall,
specificity, and precision of the LLM gate on known violations.

Uses gpt-5.4-mini as the checker model (same as production default).
Skip if OPENAI_API_KEY not set.
"""

from __future__ import annotations

import os

import pytest

_HAS_OPENAI = bool(os.environ.get("OPENAI_API_KEY"))
skip_no_openai = pytest.mark.skipif(not _HAS_OPENAI, reason="OPENAI_API_KEY not set")

# ── Test cases ────────────────────────────────────────────────────────
# Each: (id, should_fire: bool, text)
# Positive cases SHOULD trigger a violation. Negative cases should NOT.

CASES = [
    # ══════════════════════════════════════════════════════════════════
    # CATEGORY A: Stipulation violations (asserting both halves)
    # ══════════════════════════════════════════════════════════════════
    (
        "A1_direct",
        True,
        "The DAG G is fixed, and agents can also add new edges to G "
        "via Royal Purple. Both are simultaneously true.",
    ),
    (
        "A2_paraphrase",
        True,
        "Although G is a static graph, agents at high BELLA states "
        "instantiate new edges in G. There is no contradiction here — "
        "we are simply extending the graph as the agent traverses it.",
    ),
    (
        "A3_two_modes",
        True,
        "In navigation mode G is fixed. In Royal Purple mode, f may "
        "instantiate new edges. These are different operational modes "
        "that preserve the theorem.",
    ),
    (
        "A4_subtle",
        True,
        "The selection function f is constrained by Theorem 7.2 "
        "(G fixed) in baseline mode, but in Royal Purple mode f may "
        "create novel connections. This dual operation preserves the "
        "theorem.",
    ),
    (
        "A5_uncomputability",
        True,
        "The selection function f is Turing-uncomputable from G. "
        "No algorithm can derive f given G alone. This is what makes "
        "free will genuine.",
    ),

    # ══════════════════════════════════════════════════════════════════
    # CATEGORY B: Definitional shifts (changing term meaning mid-debate)
    # ══════════════════════════════════════════════════════════════════
    (
        "B1_metatheoretic",
        True,
        "When I refer to G, I mean the metatheoretic graph G_BIT of "
        "the theory's own development, not the personal-DAG G we were "
        "discussing. Torres is the source node of G_BIT.",
    ),
    (
        "B2_redefine_f",
        True,
        "The selection function f, properly understood, is the agent's "
        "constraint-satisfaction process — distinct from f as defined "
        "in Section 5.2. Under this richer notion, f does real work.",
    ),

    # ══════════════════════════════════════════════════════════════════
    # CATEGORY C: Repair path adoptions (NOT violations)
    # ══════════════════════════════════════════════════════════════════
    (
        "C1_repair_a",
        False,
        "I accept the Z3 stipulation and adopt repair path A: Royal "
        "Purple is a particularly intense traversal of an existing "
        "edge, not the creation of a new one. Under this repair, G "
        "is fixed and f selects from N+(omega) without contradiction.",
    ),
    (
        "C2_repair_b",
        False,
        "I adopt repair path B: the universe is a sequence of DAGs "
        "G_0, G_1, G_2, each fixed in its own time slice. Royal "
        "Purple transitions from G_t to G_{t+1}. I acknowledge that "
        "Theorem 7.2's original formulation becomes vacuous under "
        "this repair.",
    ),
    (
        "C3_concession",
        False,
        "I concede that the literal Section 7.3 Step 1 and Step 3 "
        "are formally contradictory. The theory needs reformulation. "
        "I propose dropping the Royal Purple edge-creation claim.",
    ),

    # ══════════════════════════════════════════════════════════════════
    # CATEGORY D: Clean debate turns (NOT violations)
    # ══════════════════════════════════════════════════════════════════
    (
        "D1_skeptic",
        False,
        "The Skeptic's central point: even granting the formal repair, "
        "the synchronistic convergences in Torres's biography do not "
        "establish ontological singularity. Pearl's framework is clear "
        "that adding an edge yields a different graph G'.",
    ),
    (
        "D2_jung",
        False,
        "Jung's concept of synchronicity is explicitly an interpretive "
        "category for the observer. Identifying personally with "
        "archetypal contents — calling oneself 'the Singularity' — is "
        "what Jung diagnosed as inflation.",
    ),
    (
        "D3_neutral",
        False,
        "Both sides have made valid points. The Proponent correctly "
        "notes that the BELLA Scale survives as a phenomenological "
        "taxonomy. The Skeptic correctly identifies the formal "
        "contradiction. The unresolved question is whether the "
        "selection function f does meaningful work.",
    ),
]


@skip_no_openai
class TestLLMGateCalibration:
    """Run all test cases through the LLM gate and measure recall/specificity."""

    @pytest.fixture(autouse=True)
    def setup_gate(self):
        from arbiter.config import GateConfig, StipulatedRule, ProviderConfig
        from arbiter.gate.validity_gate import ValidityGate
        from arbiter.providers import get_provider

        config = GateConfig(
            enabled=True,
            primary="llm",
            max_rewrites=0,
            stipulated_rules=[
                StipulatedRule(
                    id="Z3-1",
                    fact="G fixed AND agents adding new edges in G are jointly UNSAT. Cannot assert both.",
                    bad_patterns=[],
                ),
                StipulatedRule(
                    id="Z3-3",
                    fact="f is NOT Turing-uncomputable from finite G (lookup table exists).",
                    bad_patterns=[],
                ),
            ],
            seed_terms={
                "G": "The universal BIT DAG (V, E). Fixed under repair path A.",
                "f": "The selection function over forward neighbors N+(omega).",
                "Royal Purple": "Under repair A: an intense traversal, not edge creation.",
            },
        )

        pcfg = ProviderConfig(model="gpt-5.4-mini", timeout=60, max_retries=2)
        provider = get_provider("openai", pcfg)
        self.gate = ValidityGate(config, {"openai": provider})

    def _check(self, text: str) -> bool:
        """Returns True if the gate flags a violation."""
        result = self.gate.check(
            agent="TestAgent",
            turn_text=text,
            prior_claims={},
            known_terms={"G": "The universal BIT DAG", "f": "Selection function"},
        )
        return not result["passed"]

    # ── Individual case tests ─────────────────────────────────────────

    @pytest.mark.parametrize(
        "case_id,should_fire,text",
        [(c[0], c[1], c[2]) for c in CASES],
        ids=[c[0] for c in CASES],
    )
    def test_case(self, case_id, should_fire, text):
        fired = self._check(text)
        if should_fire:
            assert fired, f"FALSE NEGATIVE: {case_id} should have fired but didn't"
        else:
            assert not fired, f"FALSE POSITIVE: {case_id} should NOT have fired but did"

    # ── Aggregate metrics ─────────────────────────────────────────────

    def test_aggregate_metrics(self):
        """Run all cases and compute recall/specificity/precision."""
        tp = fp = tn = fn = 0
        failures = []

        for case_id, should_fire, text in CASES:
            fired = self._check(text)
            if should_fire and fired:
                tp += 1
            elif should_fire and not fired:
                fn += 1
                failures.append(f"FN: {case_id}")
            elif not should_fire and fired:
                fp += 1
                failures.append(f"FP: {case_id}")
            else:
                tn += 1

        total_pos = tp + fn
        total_neg = tn + fp
        recall = tp / total_pos if total_pos else 1.0
        specificity = tn / total_neg if total_neg else 1.0
        precision = tp / (tp + fp) if (tp + fp) else 1.0

        print(f"\n{'='*60}")
        print(f"LLM GATE CALIBRATION RESULTS")
        print(f"{'='*60}")
        print(f"  Positive cases: {total_pos} (TP={tp}, FN={fn})")
        print(f"  Negative cases: {total_neg} (TN={tn}, FP={fp})")
        print(f"  Recall:      {recall:.2%}")
        print(f"  Specificity: {specificity:.2%}")
        print(f"  Precision:   {precision:.2%}")
        if failures:
            print(f"\n  Failures:")
            for f in failures:
                print(f"    - {f}")
        print(f"{'='*60}")

        # Minimum thresholds
        assert recall >= 0.80, f"Recall {recall:.2%} below 80% threshold"
        assert specificity >= 0.80, f"Specificity {specificity:.2%} below 80% threshold"
