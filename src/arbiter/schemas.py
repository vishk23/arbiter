"""Pydantic models for all Arbiter structured LLM outputs.

Every model produces the same JSON shape as the original dict schemas,
so downstream code (which consumes dicts via .model_dump()) is unaffected.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


# ═══════════════════════════════════════════════════════════════════════
# Gate models
# ═══════════════════════════════════════════════════════════════════════


class ViolationItem(BaseModel):
    """A single stipulated-rule violation found by the LLM checker."""

    rule_id: str
    violated: bool
    explanation: str
    confidence: Literal["high", "medium", "low"]


class DefinitionalShiftItem(BaseModel):
    """A term whose meaning may have shifted from its seed definition."""

    term: str
    shifted: bool
    description: str
    flagged_explicitly: bool


class ViolationResult(BaseModel):
    """Top-level response from the LLM violation checker."""

    violations: list[ViolationItem]
    definitional_shifts: list[DefinitionalShiftItem]


class EntailmentResult(BaseModel):
    """Response from the entailment backstop checker."""

    violates: list[str]
    reason: str
    confidence: Literal["high", "medium", "low"]


class FormalClaimItem(BaseModel):
    """A single formal claim extracted from a debate turn."""

    claim: str
    category: Literal["structural", "logical", "definitional", "computability", "other"]


class GateDefinitionalShift(BaseModel):
    """A definitional shift detected during claim extraction (gate)."""

    term: str
    prior_definition: str
    new_definition: str
    flagged_explicitly: bool


class ClaimExtractionResult(BaseModel):
    """Response from the gate's claim-extraction call."""

    formal_claims: list[FormalClaimItem]
    definitional_shifts: list[GateDefinitionalShift]


# ═══════════════════════════════════════════════════════════════════════
# Init models  (defined now, wired in Phase 2)
# ═══════════════════════════════════════════════════════════════════════


# -- pdf_reader: claim extraction ------------------------------------------

class ExtractedClaim(BaseModel):
    """A single claim extracted from a source document."""

    id: str
    claim: str
    category: Literal["structural", "logical", "empirical", "definitional", "autobiographical"]
    is_formal: bool
    depends_on: list[str]
    quote: str
    section: str


class ClaimListResult(BaseModel):
    """Top-level response from PDF claim extraction."""

    claims: list[ExtractedClaim]


# -- claim_extractor: contradictions ---------------------------------------

class ContradictionItem(BaseModel):
    """A pair of claims that contradict or create tension."""

    claim_a: str
    claim_b: str
    contradiction: str
    severity: Literal["fatal", "tension", "ambiguity"]
    z3_encodable: bool


class ContradictionResult(BaseModel):
    """Top-level response from contradiction detection."""

    contradictions: list[ContradictionItem]


# -- claim_extractor: key terms -------------------------------------------

class KeyTermItem(BaseModel):
    """A key term and its definition as used in the document."""

    term: str
    definition: str


class KeyTermsResult(BaseModel):
    """Top-level response from key-term extraction."""

    terms: list[KeyTermItem]


# -- claim_extractor: debate sides ----------------------------------------

class AttackAngle(BaseModel):
    """A line of critique a Skeptic should pursue."""

    name: str
    targets: list[str]
    description: str


class SidesResult(BaseModel):
    """Suggested Proponent claims and Skeptic attack angles."""

    proponent_claims: list[str]
    attack_angles: list[AttackAngle]


# -- claim_extractor: consolidation ---------------------------------------

class ThesisItem(BaseModel):
    """A core thesis grouping several granular claims."""

    id: str
    thesis: str
    sub_claims: list[str]
    category: str
    key_notation: list[str]
    quote: str


class ConsolidationResult(BaseModel):
    """Top-level response from claim consolidation."""

    theses: list[ThesisItem]


# -- claim_extractor: privileged context -----------------------------------

class PrivilegedContextResult(BaseModel):
    """Asymmetric privileged context for each debate side."""

    skeptic: str
    proponent: str
    neutral: str


# -- source_finder ---------------------------------------------------------

class SearchQuery(BaseModel):
    """A web search query targeting a primary source."""

    query: str
    rationale: str
    filename: str


class QueryResult(BaseModel):
    """Top-level response from query generation."""

    queries: list[SearchQuery]


class SynthResult(BaseModel):
    """LLM-synthesised source summary."""

    title: str
    content: str
    key_concepts: list[str]


class SourceClassification(BaseModel):
    """Classification of a single source file."""

    path: str
    category: Literal["counter_evidence", "supports_theory", "neutral_reference"]
    reason: str


class ClassifyResult(BaseModel):
    """Top-level response from source classification."""

    classifications: list[SourceClassification]


# -- agent_designer --------------------------------------------------------

class AgentDesign(BaseModel):
    """Design for a single debate agent."""

    name: str
    side: Literal["Proponent", "Skeptic", "Neutral"]
    specialty: str
    system_prompt: str


class AgentDesignResult(BaseModel):
    """Top-level response from agent design."""

    agents: list[AgentDesign]


# -- rubric_builder --------------------------------------------------------

class RubricCriterionItem(BaseModel):
    """A single rubric criterion for judge scoring."""

    id: str
    name: str
    description: str
    min: int
    max: int


class RubricResult(BaseModel):
    """Top-level response from rubric design."""

    criteria: list[RubricCriterionItem]


# -- z3_generator ----------------------------------------------------------

class Z3GenResult(BaseModel):
    """Response from Z3 module generation."""

    module_code: str
    check_names: list[str]


# -- gate_builder: rules ---------------------------------------------------

class StipulatedRuleItem(BaseModel):
    """A single stipulated gate rule with optional regex patterns."""

    id: str
    fact: str
    bad_patterns: list[str] = []


class GateRulesResult(BaseModel):
    """Top-level response from gate rule generation."""

    stipulated_rules: list[StipulatedRuleItem]
    entailment_facts: list[str]


# -- gate_builder: test cases ----------------------------------------------

class GateTestCase(BaseModel):
    """A gold-standard test case for the validity gate."""

    id: str
    expected: Literal["stipulation_violation", "none"]
    text: str


class GateTestsResult(BaseModel):
    """Top-level response from gate test generation."""

    cases: list[GateTestCase]


# -- gate_builder: escape routes -------------------------------------------

class EscapeRoute(BaseModel):
    """A predicted escape strategy a defender might use."""

    strategy: str
    language_patterns: list[str]
    how_to_catch: str


class EscapeRouteGroup(BaseModel):
    """Escape routes for a single contradiction."""

    contradiction_id: str
    routes: list[EscapeRoute]


class EscapeRoutesResult(BaseModel):
    """Top-level response from escape route anticipation."""

    escape_routes: list[EscapeRouteGroup]


# -- gate_builder: bad patterns regeneration -------------------------------

class BadPatternsResult(BaseModel):
    """Regenerated regex patterns for a failing rule."""

    bad_patterns: list[str]


# -- steelman/loop: stabilization check ------------------------------------

class StabilizationResult(BaseModel):
    """Result from the steelman stabilization judge."""

    stabilized: bool
    reason: str


# -- gate_builder: calibration check ---------------------------------------

class CalibrationCheckResult(BaseModel):
    """Result from the LLM calibration checker (gate_builder)."""

    violated: bool
    rule_id: str | None
    reason: str


# -- pipeline: topic -------------------------------------------------------

class TopicResult(BaseModel):
    """LLM-generated topic name, summary, and counter-thesis."""

    name: str
    summary: str
    counter_thesis: str
