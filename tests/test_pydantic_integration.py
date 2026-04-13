"""Integration tests: Pydantic structured output with real LLM calls.

Validates that every Pydantic model in schemas.py produces valid output
when passed through call_structured() with a real provider. Catches
field mismatches, missing required fields, and schema-model divergence
that unit tests with mocks cannot detect.

Requires OPENAI_API_KEY in .env or environment.
"""

from __future__ import annotations

import os

import pytest

_HAS_OPENAI = bool(os.environ.get("OPENAI_API_KEY"))
skip_no_openai = pytest.mark.skipif(not _HAS_OPENAI, reason="OPENAI_API_KEY not set")


@pytest.fixture(scope="module")
def provider():
    """Shared OpenAI provider for all tests (gpt-5.4-mini for cost)."""
    from arbiter.config import ProviderConfig
    from arbiter.providers import get_provider

    cfg = ProviderConfig(model="gpt-5.4-mini", timeout=60, max_retries=2)
    return get_provider("openai", cfg)


# ═══════════════════════════════════════════════════════════════════════
# Gate schemas (Phase 1 — already tested via calibration, but verify
# the Pydantic path specifically)
# ═══════════════════════════════════════════════════════════════════════


@skip_no_openai
class TestGateSchemas:
    """Verify gate Pydantic models with real LLM."""

    def test_violation_result(self, provider):
        from arbiter.schemas import ViolationResult

        result = provider.call_structured(
            system="Check if text violates: [R1] Water is wet.",
            user="TEXT: Water is dry and also wet at the same time.",
            schema=ViolationResult,
            max_tokens=1000,
        )
        assert "violations" in result
        assert "definitional_shifts" in result
        assert isinstance(result["violations"], list)

    def test_entailment_result(self, provider):
        from arbiter.schemas import EntailmentResult

        result = provider.call_structured(
            system="Check if text contradicts: Water is always wet.",
            user="TEXT: Water is dry.",
            schema=EntailmentResult,
            max_tokens=500,
        )
        assert "violates" in result
        assert "confidence" in result
        assert result["confidence"] in ("high", "medium", "low")

    def test_claim_extraction_result(self, provider):
        from arbiter.schemas import ClaimExtractionResult

        result = provider.call_structured(
            system="Extract formal claims and definitional shifts.",
            user="The graph G is fixed. Agent f selects edges from N+(omega).",
            schema=ClaimExtractionResult,
            max_tokens=1000,
        )
        assert "formal_claims" in result
        assert "definitional_shifts" in result


# ═══════════════════════════════════════════════════════════════════════
# Init schemas (Phase 2 — NEVER tested with real LLM before)
# ═══════════════════════════════════════════════════════════════════════


@skip_no_openai
class TestInitSchemas:
    """Verify every init Pydantic model with real LLM output."""

    def test_topic_result(self, provider):
        from arbiter.schemas import TopicResult

        result = provider.call_structured(
            system="Generate a debate topic with name, summary, counter_thesis.",
            user="Topic: Whether artificial consciousness is possible.",
            schema=TopicResult,
            max_tokens=2000,
        )
        assert result["name"]
        assert result["summary"]
        assert result["counter_thesis"]

    def test_claim_list_result(self, provider):
        from arbiter.schemas import ClaimListResult

        result = provider.call_structured(
            system=(
                "Extract claims from text. Each claim needs: id, claim, "
                "category (structural/logical/empirical/definitional/autobiographical), "
                "is_formal, depends_on, quote, section."
            ),
            user=(
                "The brain is a computational system (Section 1). "
                "Consciousness emerges from information integration (Section 2). "
                "Therefore consciousness is computable (Section 3)."
            ),
            schema=ClaimListResult,
            max_tokens=2000,
        )
        assert "claims" in result
        assert len(result["claims"]) >= 1
        c = result["claims"][0]
        assert "id" in c
        assert "claim" in c
        assert "category" in c
        assert c["category"] in ("structural", "logical", "empirical", "definitional", "autobiographical")

    def test_contradiction_result(self, provider):
        from arbiter.schemas import ContradictionResult

        result = provider.call_structured(
            system=(
                "Find contradictions between claims. Each needs: claim_a, claim_b, "
                "contradiction, severity (fatal/tension/ambiguity), z3_encodable."
            ),
            user=(
                "C1: The system is deterministic. "
                "C2: The system has genuine free will. "
                "Find contradictions."
            ),
            schema=ContradictionResult,
            max_tokens=1000,
        )
        assert "contradictions" in result
        assert len(result["contradictions"]) >= 1
        c = result["contradictions"][0]
        assert c["severity"] in ("fatal", "tension", "ambiguity")

    def test_key_terms_result(self, provider):
        from arbiter.schemas import KeyTermsResult

        result = provider.call_structured(
            system="Extract key terms with definitions.",
            user="C1: The DAG G=(V,E) is fixed. C2: Function f selects from N+(omega).",
            schema=KeyTermsResult,
            max_tokens=1000,
        )
        assert "terms" in result
        assert len(result["terms"]) >= 1
        assert "term" in result["terms"][0]
        assert "definition" in result["terms"][0]

    def test_sides_result(self, provider):
        from arbiter.schemas import SidesResult

        result = provider.call_structured(
            system=(
                "Suggest proponent_claims (list of IDs) and attack_angles "
                "(each with name, targets, description)."
            ),
            user=(
                "C1: Consciousness is computable. C2: Qualia are irreducible. "
                "C3: The brain is a Turing machine."
            ),
            schema=SidesResult,
            max_tokens=1500,
        )
        assert "proponent_claims" in result
        assert "attack_angles" in result
        assert isinstance(result["attack_angles"], list)

    def test_consolidation_result(self, provider):
        from arbiter.schemas import ConsolidationResult

        result = provider.call_structured(
            system=(
                "Group claims into core theses. Each thesis needs: "
                "id, thesis, sub_claims, category, key_notation, quote."
            ),
            user=(
                "C1: The graph is fixed. C2: Edges pre-exist. C3: Agents traverse. "
                "C4: Consciousness emerges. C5: States are ordered. "
                "Group into 1-3 theses."
            ),
            schema=ConsolidationResult,
            max_tokens=2000,
        )
        assert "theses" in result
        assert len(result["theses"]) >= 1
        t = result["theses"][0]
        assert "id" in t
        assert "thesis" in t
        assert "sub_claims" in t

    def test_privileged_context_result(self, provider):
        from arbiter.schemas import PrivilegedContextResult

        result = provider.call_structured(
            system="Build privileged context for skeptic, proponent, neutral.",
            user="Theory claims consciousness is computable. Counter: qualia are irreducible.",
            schema=PrivilegedContextResult,
            max_tokens=2000,
        )
        assert result["skeptic"]
        assert result["proponent"]
        assert result["neutral"]

    def test_query_result(self, provider):
        from arbiter.schemas import QueryResult

        result = provider.call_structured(
            system="Generate 2 web search queries. Each needs: query, rationale, filename.",
            user="Theory about consciousness and computation. Find primary sources.",
            schema=QueryResult,
            max_tokens=1000,
        )
        assert "queries" in result
        assert len(result["queries"]) >= 1
        q = result["queries"][0]
        assert "query" in q
        assert "rationale" in q
        assert "filename" in q

    def test_synth_result(self, provider):
        from arbiter.schemas import SynthResult

        result = provider.call_structured(
            system="Summarize a source. Return title, content, key_concepts.",
            user="Summarize Tononi's Integrated Information Theory (IIT).",
            schema=SynthResult,
            max_tokens=2000,
        )
        assert result["title"]
        assert result["content"]
        assert isinstance(result["key_concepts"], list)

    def test_classify_result(self, provider):
        from arbiter.schemas import ClassifyResult

        result = provider.call_structured(
            system=(
                "Classify sources. Each needs: path, "
                "category (counter_evidence/supports_theory/neutral_reference), reason."
            ),
            user=(
                "FILE: /sources/tononi_iit.txt\n"
                "IIT argues consciousness requires integrated information...\n\n"
                "Classify this source for a debate about computational consciousness."
            ),
            schema=ClassifyResult,
            max_tokens=500,
        )
        assert "classifications" in result
        assert len(result["classifications"]) >= 1
        c = result["classifications"][0]
        assert c["category"] in ("counter_evidence", "supports_theory", "neutral_reference")

    def test_agent_design_result(self, provider):
        from arbiter.schemas import AgentDesignResult

        result = provider.call_structured(
            system=(
                "Design 2 debate agents. Each needs: name (PascalCase), "
                "side (Proponent/Skeptic/Neutral), specialty, system_prompt."
            ),
            user="Design agents for a debate about whether P=NP.",
            schema=AgentDesignResult,
            max_tokens=2000,
        )
        assert "agents" in result
        assert len(result["agents"]) >= 1
        a = result["agents"][0]
        assert a["side"] in ("Proponent", "Skeptic", "Neutral")
        assert a["system_prompt"]

    def test_rubric_result(self, provider):
        from arbiter.schemas import RubricResult

        result = provider.call_structured(
            system=(
                "Design 3 rubric criteria. Each needs: "
                "id, name (snake_case), description, min (int), max (int)."
            ),
            user="Design rubric for a debate about AI consciousness.",
            schema=RubricResult,
            max_tokens=1500,
        )
        assert "criteria" in result
        assert len(result["criteria"]) >= 1
        c = result["criteria"][0]
        assert "id" in c
        assert "name" in c
        assert isinstance(c["min"], int)
        assert isinstance(c["max"], int)

    def test_z3_gen_result(self, provider):
        from arbiter.schemas import Z3GenResult

        result = provider.call_structured(
            system="Generate a Z3 module. Return module_code and check_names.",
            user=(
                "Contradiction: 'G is fixed' AND 'agents create new edges'. "
                "Generate a simple Z3 check."
            ),
            schema=Z3GenResult,
            max_tokens=3000,
        )
        assert result["module_code"]
        assert isinstance(result["check_names"], list)

    def test_gate_rules_result(self, provider):
        from arbiter.schemas import GateRulesResult

        result = provider.call_structured(
            system=(
                "Generate gate rules. Return stipulated_rules "
                "(each with id, fact, bad_patterns) and entailment_facts."
            ),
            user="Contradiction: determinism AND free will are jointly UNSAT.",
            schema=GateRulesResult,
            max_tokens=1500,
        )
        assert "stipulated_rules" in result
        assert "entailment_facts" in result
        assert len(result["stipulated_rules"]) >= 1

    def test_gate_tests_result(self, provider):
        from arbiter.schemas import GateTestsResult

        result = provider.call_structured(
            system=(
                "Generate test cases. Each needs: id, "
                "expected (stipulation_violation/none), text."
            ),
            user=(
                "Rule: [R1] Determinism AND free will are jointly UNSAT. "
                "Generate 2 test cases: 1 violation, 1 clean."
            ),
            schema=GateTestsResult,
            max_tokens=1500,
        )
        assert "cases" in result
        assert len(result["cases"]) >= 1
        c = result["cases"][0]
        assert c["expected"] in ("stipulation_violation", "none")

    def test_escape_routes_result(self, provider):
        from arbiter.schemas import EscapeRoutesResult

        result = provider.call_structured(
            system=(
                "Predict escape routes. Return escape_routes, each with "
                "contradiction_id and routes (strategy, language_patterns, how_to_catch)."
            ),
            user="Contradiction C1: determinism vs free will. Predict 2 escape routes.",
            schema=EscapeRoutesResult,
            max_tokens=1500,
        )
        assert "escape_routes" in result
        assert len(result["escape_routes"]) >= 1

    def test_stabilization_result(self, provider):
        from arbiter.schemas import StabilizationResult

        result = provider.call_structured(
            system="Compare two versions. Return stabilized (bool) and reason.",
            user=(
                "VERSION A: The theory holds that X implies Y.\n"
                "VERSION B: The theory holds that X implies Y, with minor wording changes.\n"
                "Are these stabilized?"
            ),
            schema=StabilizationResult,
            max_tokens=500,
        )
        assert "stabilized" in result
        assert isinstance(result["stabilized"], bool)
        assert "reason" in result

    def test_calibration_check_result(self, provider):
        from arbiter.schemas import CalibrationCheckResult

        result = provider.call_structured(
            system=(
                "Check if text violates: [R1] Water is wet. "
                "Return violated (bool), rule_id (string or null), reason."
            ),
            user="TEXT: Water is completely dry.",
            schema=CalibrationCheckResult,
            max_tokens=500,
        )
        assert "violated" in result
        assert isinstance(result["violated"], bool)
        assert "reason" in result


# ═══════════════════════════════════════════════════════════════════════
# Multi-provider Pydantic path tests
# ═══════════════════════════════════════════════════════════════════════

_HAS_ANTHROPIC = bool(os.environ.get("ANTHROPIC_API_KEY"))
_HAS_GEMINI = bool(os.environ.get("GEMINI_API_KEY"))

skip_no_anthropic = pytest.mark.skipif(not _HAS_ANTHROPIC, reason="ANTHROPIC_API_KEY not set")
skip_no_gemini = pytest.mark.skipif(not _HAS_GEMINI, reason="GEMINI_API_KEY not set")


@skip_no_anthropic
class TestAnthropicPydantic:
    """Verify Anthropic tool-use Pydantic path with real API."""

    @pytest.fixture
    def anthropic_provider(self):
        from arbiter.config import ProviderConfig
        from arbiter.providers import get_provider

        cfg = ProviderConfig(model="claude-haiku-4-5-20251001", timeout=60, max_retries=2)
        return get_provider("anthropic", cfg)

    def test_violation_result(self, anthropic_provider):
        from arbiter.schemas import ViolationResult

        result = anthropic_provider.call_structured(
            system="Check if text violates: [R1] Water is wet.",
            user="TEXT: Water is both wet and dry simultaneously.",
            schema=ViolationResult,
            max_tokens=1000,
        )
        assert "violations" in result
        assert "definitional_shifts" in result

    def test_claim_list_result(self, anthropic_provider):
        from arbiter.schemas import ClaimListResult

        result = anthropic_provider.call_structured(
            system=(
                "Extract claims. Each: id, claim, "
                "category (structural/logical/empirical/definitional/autobiographical), "
                "is_formal, depends_on, quote, section."
            ),
            user="The brain is computational (Section 1). Consciousness emerges (Section 2).",
            schema=ClaimListResult,
            max_tokens=2000,
        )
        assert "claims" in result
        assert len(result["claims"]) >= 1

    def test_topic_result(self, anthropic_provider):
        from arbiter.schemas import TopicResult

        result = anthropic_provider.call_structured(
            system="Generate a debate topic: name, summary, counter_thesis.",
            user="Topic: Is mathematics invented or discovered?",
            schema=TopicResult,
            max_tokens=2000,
        )
        assert result["name"]
        assert result["summary"]
        assert result["counter_thesis"]


@skip_no_gemini
class TestGeminiPydantic:
    """Verify Google Gemini native Pydantic path with real API."""

    @pytest.fixture
    def gemini_provider(self):
        from arbiter.config import ProviderConfig
        from arbiter.providers import get_provider

        cfg = ProviderConfig(model="gemini-3-flash-preview", timeout=60, max_retries=2)
        return get_provider("google", cfg)

    def test_violation_result(self, gemini_provider):
        from arbiter.schemas import ViolationResult

        result = gemini_provider.call_structured(
            system="Check if text violates: [R1] Water is wet.",
            user="TEXT: Water is both wet and dry simultaneously.",
            schema=ViolationResult,
            max_tokens=2000,
        )
        assert "violations" in result
        assert "definitional_shifts" in result

    def test_topic_result(self, gemini_provider):
        from arbiter.schemas import TopicResult

        result = gemini_provider.call_structured(
            system="Generate a debate topic: name, summary, counter_thesis.",
            user="Topic: Should AI have legal rights?",
            schema=TopicResult,
            max_tokens=2000,
        )
        assert result["name"]
        assert result["summary"]
        assert result["counter_thesis"]
