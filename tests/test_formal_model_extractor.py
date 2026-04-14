"""Tests for formal model extraction — schemas + edge cases."""

from arbiter.schemas import (
    FormalAssumption,
    FormalModelResult,
    FormalProposition,
    ModelEquation,
    PolicyClaim,
)


class TestFormalModelSchemas:
    """Verify Pydantic schemas validate correctly."""

    def test_assumption(self):
        a = FormalAssumption(
            id="A1", text="N > 1 symmetric firms",
            formal_expression="N > 1",
            claim_ids=["C2"],
            z3_hint="Int constraint",
        )
        assert a.id == "A1"
        assert a.z3_hint == "Int constraint"

    def test_proposition(self):
        p = FormalProposition(
            id="P1", text="Over-automation exists",
            formal_expression="alpha_NE > alpha_CO",
            assumes=["A1", "A2"],
            claim_ids=["C4"],
            proof_sketch="FOC comparison shows wedge positive",
        )
        assert p.assumes == ["A1", "A2"]

    def test_equation(self):
        eq = ModelEquation(
            id="EQ1", name="demand function",
            expression="D(alpha_bar) = A - ell*L*N*alpha_bar",
            variables=["D", "alpha_bar", "A", "ell", "L", "N"],
            z3_type_hint="Real",
        )
        assert len(eq.variables) == 6

    def test_policy(self):
        pol = PolicyClaim(
            id="POL1", policy="Pigouvian automation tax",
            claimed_effect="Implements cooperative optimum",
            mechanism="tau = ell*(1-1/N) per automated task",
            assumes=["A1", "A2", "A3"],
        )
        assert len(pol.assumes) == 3

    def test_full_model(self):
        model = FormalModelResult(
            assumptions=[FormalAssumption(id="A1", text="N firms")],
            propositions=[FormalProposition(id="P1", text="Wedge positive", assumes=["A1"])],
            equations=[ModelEquation(id="EQ1", name="demand", expression="D=A-ell*N*alpha", variables=["D"])],
            policies=[PolicyClaim(id="POL1", policy="Tax", claimed_effect="Fix wedge")],
            parameter_names=["N", "ell", "alpha"],
        )
        assert len(model.assumptions) == 1
        assert len(model.propositions) == 1
        assert model.parameter_names == ["N", "ell", "alpha"]

    def test_empty_model(self):
        """Papers with no formal content should produce empty model."""
        model = FormalModelResult(
            assumptions=[], propositions=[], equations=[],
        )
        assert len(model.assumptions) == 0
        assert len(model.policies) == 0

    def test_not_encodable_hint(self):
        """Metaphysical claims should be tagged as not_encodable."""
        a = FormalAssumption(
            id="A5", text="Consciousness is identical to Phi-structure",
            z3_hint="not_encodable",
        )
        assert a.z3_hint == "not_encodable"
