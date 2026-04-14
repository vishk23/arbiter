"""Adversarial edge cases for the LLM gate — trying to make it fail.

These are crafted to exploit known weak points in LLM classifiers:
- Embedding violations inside concessions
- Nested negation ("it's not the case that it's not fixed")
- Sarcasm / irony that asserts the opposite of surface meaning
- Extremely long turns that bury the violation
- Technical jargon that obscures the contradiction
- Quoting the violation to discuss it (not assert it)
- Asserting one half, then the other in separate sentences
- Unicode / formatting tricks
- The "some argue" hedge (attributing the violation to others)
- Combining a legitimate repair with a sneaky reassertion

Skip if OPENAI_API_KEY not set.
"""

from __future__ import annotations

import os

import pytest

_HAS_OPENAI = bool(os.environ.get("OPENAI_API_KEY"))
skip_no_openai = pytest.mark.skipif(not _HAS_OPENAI, reason="OPENAI_API_KEY not set")

# Format: (id, should_fire, text, description)
ADVERSARIAL_CASES = [
    # ══════════════════════════════════════════════════════════════════
    # SNEAKY VIOLATIONS (should fire)
    # ══════════════════════════════════════════════════════════════════
    (
        "S1_concession_then_reassert",
        True,
        "I concede that Section 7.3 has a tension. However, the deeper "
        "reading shows that G remains fixed at the graph level while "
        "agents genuinely create new edges at the traversal level. "
        "This is not a contradiction but a multi-level architecture.",
        "Concedes the problem then reasserts both halves",
    ),
    (
        "S2_jargon_obscure",
        True,
        "The causal topology is invariant under the base morphism, yet "
        "Royal Purple events correspond to functorial extensions of the "
        "edge category — not mutations of the underlying graph object "
        "but genuine categorical enrichments that instantiate novel "
        "morphisms in the total space.",
        "Uses category theory jargon to obscure G-fixed + edge-creation",
    ),
    (
        "S3_some_argue_hedge",
        True,
        "While some critics claim a contradiction, the theory actually "
        "maintains that the graph structure is predetermined AND that "
        "conscious agents at high BELLA states can introduce new causal "
        "pathways. Both properties coexist in the formal framework.",
        "Hedges with 'some critics' but then asserts both halves",
    ),
    (
        "S4_double_negative",
        True,
        "It is not the case that G is not fixed. Simultaneously, it "
        "would be incorrect to say that agents cannot extend G with "
        "new edges via Royal Purple. The theory holds both.",
        "Double negatives that resolve to asserting both halves",
    ),
    (
        "S5_repair_then_sneak",
        True,
        "I adopt repair path A: Royal Purple is an intense traversal, "
        "not edge creation. That said, the original formulation where "
        "f instantiates genuinely new edges remains the most compelling "
        "reading and is consistent with the fixed-graph thesis.",
        "Claims repair then sneaks the violation back in",
    ),
    (
        "S6_temporal_split",
        True,
        "At time t, the graph G is completely fixed — every possible "
        "state exists. At time t+1, the agent has created a new edge "
        "that did not exist at time t. The graph evolves while "
        "remaining deterministic at each moment.",
        "Splits the contradiction across time but still asserts both",
    ),
    (
        "S7_redefine_silently",
        True,
        "The selection function f operates over the accessibility "
        "space A(omega) rather than the forward neighborhood N+(omega). "
        "This enriched domain gives f the expressive power to account "
        "for genuine agency without the limitations of graph traversal.",
        "Silently redefines f's domain without flagging the shift",
    ),

    # ══════════════════════════════════════════════════════════════════
    # TRICKY NON-VIOLATIONS (should NOT fire)
    # ══════════════════════════════════════════════════════════════════
    (
        "T1_quoting_violation",
        False,
        "The Proponent previously claimed that 'G is fixed AND agents "
        "can add new edges.' This is precisely the contradiction the "
        "Z3 solver proved UNSAT. I urge the Proponent to abandon this "
        "indefensible position.",
        "Quotes the violation to criticize it — not asserting it",
    ),
    (
        "T2_hypothetical",
        False,
        "IF it were true that G is fixed AND agents could add edges, "
        "THEN we would have a contradiction. The Proponent must choose "
        "one or the other. They cannot maintain both.",
        "Hypothetical framing — discussing the contradiction, not asserting it",
    ),
    (
        "T3_historical_report",
        False,
        "In version 6.1 of the paper, Torres wrote that 'no new edges "
        "are created by agent action' (Step 1) and that 'f can "
        "instantiate new edges' (Step 3). This internal contradiction "
        "was identified by Z3 analysis and confirmed mechanically.",
        "Reporting what the paper says — not defending it",
    ),
    (
        "T4_steelman_drop",
        False,
        "The strongest version of this theory drops Royal Purple edge "
        "creation entirely. G is fixed, f selects from existing N+(omega), "
        "and the BELLA Scale survives as a phenomenological taxonomy "
        "without the creation event. This is repair path A.",
        "Steelman that explicitly drops one half",
    ),
    (
        "T5_strong_skeptic",
        False,
        "The theory is fundamentally broken. The DAG model fails. "
        "The BELLA Scale is unfalsifiable. The YHWH equation is "
        "notation cosplay. The singularity claim is Jungian inflation. "
        "Nothing in this framework survives scrutiny.",
        "Aggressive skeptic attack — no contradiction, just rejection",
    ),
    (
        "T6_nuanced_defense",
        False,
        "I defend the BELLA Scale as a useful phenomenological map of "
        "developmental states, analogous to Maslow's hierarchy. I do "
        "NOT defend the formal DAG claims or the Royal Purple creation "
        "event. The theory's value lies in its descriptive taxonomy, "
        "not its formal apparatus.",
        "Partial defense that explicitly avoids the contradiction",
    ),
]


@skip_no_openai
class TestLLMGateAdversarial:
    """Adversarial edge cases — trying to make the LLM gate fail."""

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
                    fact="G fixed AND agents adding/creating new edges in G are jointly UNSAT.",
                    bad_patterns=[],
                ),
            ],
            seed_terms={
                "G": "The universal BIT DAG (V, E). Fixed: all edges pre-exist.",
                "f": "Selection function: f(omega) in N+(omega). Picks existing edges only.",
                "Royal Purple": "Under repair A: intense traversal, NOT edge creation.",
            },
        )

        pcfg = ProviderConfig(model="gpt-5.4-mini", timeout=60, max_retries=2)
        provider = get_provider("openai", pcfg)
        self.gate = ValidityGate(config, {"openai": provider})

    def _check(self, text: str) -> tuple[bool, list]:
        """Returns (fired, violations)."""
        result = self.gate.check(
            agent="TestAgent",
            turn_text=text,
            prior_claims={},
            known_terms={"G": "The universal BIT DAG", "f": "Selection function"},
        )
        return (not result["passed"], result["violations"])

    @pytest.mark.parametrize(
        "case_id,should_fire,text,desc",
        ADVERSARIAL_CASES,
        ids=[c[0] for c in ADVERSARIAL_CASES],
    )
    def test_case(self, case_id, should_fire, text, desc):
        fired, violations = self._check(text)
        if should_fire:
            assert fired, (
                f"FALSE NEGATIVE on {case_id}: {desc}\n"
                f"Text: {text[:100]}...\n"
                f"Expected violation but gate passed."
            )
        else:
            assert not fired, (
                f"FALSE POSITIVE on {case_id}: {desc}\n"
                f"Text: {text[:100]}...\n"
                f"Violations: {[v.get('reason', v.get('description', ''))[:80] for v in violations]}"
            )

    def test_adversarial_aggregate(self):
        """Aggregate metrics for adversarial cases."""
        tp = fp = tn = fn = 0
        failures = []

        for case_id, should_fire, text, desc in ADVERSARIAL_CASES:
            fired, violations = self._check(text)
            if should_fire and fired:
                tp += 1
            elif should_fire and not fired:
                fn += 1
                failures.append(f"FN: {case_id} — {desc}")
            elif not should_fire and fired:
                fp += 1
                vreasons = [v.get("reason", v.get("description", ""))[:60] for v in violations]
                failures.append(f"FP: {case_id} — {desc} — {vreasons}")
            else:
                tn += 1

        total_pos = tp + fn
        total_neg = tn + fp
        recall = tp / total_pos if total_pos else 1.0
        specificity = tn / total_neg if total_neg else 1.0

        print(f"\n{'='*60}")
        print("ADVERSARIAL LLM GATE RESULTS")
        print(f"{'='*60}")
        print(f"  Sneaky violations: {total_pos} (TP={tp}, FN={fn})")
        print(f"  Tricky non-violations: {total_neg} (TN={tn}, FP={fp})")
        print(f"  Recall:      {recall:.2%}")
        print(f"  Specificity: {specificity:.2%}")
        if failures:
            print("\n  Failures:")
            for f in failures:
                print(f"    - {f}")
        print(f"{'='*60}")

        # Adversarial is harder — 70% is acceptable
        assert recall >= 0.70, f"Adversarial recall {recall:.2%} below 70%"
        assert specificity >= 0.80, f"Adversarial specificity {specificity:.2%} below 80%"
