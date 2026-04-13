"""Higher-level claim analysis: contradictions, key terms, debate sides, consolidation."""

from __future__ import annotations

import json
import logging
import textwrap
from typing import TYPE_CHECKING

from arbiter.schemas import (
    ContradictionResult,
    ConsolidationResult,
    KeyTermsResult,
    PrivilegedContextResult,
    SidesResult,
)

if TYPE_CHECKING:
    from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _claims_summary(claims: list[dict]) -> str:
    """Render a compact text summary of claims for inclusion in prompts."""
    lines: list[str] = []
    for c in claims:
        deps = ", ".join(c.get("depends_on", []))
        formal = "formal" if c.get("is_formal") else "informal"
        lines.append(
            f'{c["id"]} [{c.get("category", "?")}] ({formal})'
            f'{" depends:" + deps if deps else ""}\n'
            f'  "{c["claim"]}"'
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Contradiction detection
# ---------------------------------------------------------------------------

_CONTRADICTION_SYSTEM = textwrap.dedent("""\
    You are an expert logician and critical analyst.  Given a numbered list
    of claims extracted from a single document, your task is to identify
    ALL potential internal contradictions, tensions, or ambiguities between
    pairs of claims.

    Rules:
    1. Be thorough -- check every plausible pair.
    2. A "fatal" contradiction means the two claims cannot both be true
       under any reasonable interpretation.
    3. A "tension" means the claims push in opposite directions but might
       be reconciled with careful qualification.
    4. An "ambiguity" means the apparent conflict may be caused by vague
       or undefined terminology.
    5. Set ``z3_encodable`` to true only when both claims involve
       formal/structural assertions that could be translated into SMT
       constraints.

    Return a JSON object matching the provided schema.
""")


def identify_contradictions(
    claims: list[dict],
    provider: "BaseProvider",
    *,
    max_tokens: int = 8000,
) -> list[dict]:
    """Ask the LLM to find potential internal contradictions among *claims*.

    Returns a list of contradiction dicts (see ``ContradictionResult``).
    """
    summary = _claims_summary(claims)
    user_msg = (
        "Here are the extracted claims from a document.  "
        "Identify all internal contradictions, tensions, and ambiguities.\n\n"
        f"{summary}"
    )
    result = provider.call_structured(
        system=_CONTRADICTION_SYSTEM,
        user=user_msg,
        schema=ContradictionResult,
        max_tokens=max_tokens,
    )
    return result.get("contradictions", [])


# ---------------------------------------------------------------------------
# Key-term extraction
# ---------------------------------------------------------------------------

_KEY_TERMS_SYSTEM = textwrap.dedent("""\
    You are a careful reader and lexicographer.  Given a numbered list of
    claims from a document, extract every key term or concept that carries
    specialised meaning in the author's framework.

    For each term, provide a concise definition that reflects how the
    author uses it (not necessarily standard usage).

    Return a JSON object matching the provided schema.
""")


def identify_key_terms(
    claims: list[dict],
    provider: "BaseProvider",
    *,
    max_tokens: int = 4000,
) -> dict[str, str]:
    """Extract key terms and their definitions from the claims.

    Returns ``{term: definition}`` suitable for seeding debate gates.
    """
    summary = _claims_summary(claims)
    user_msg = (
        "Extract all key terms and their definitions from these claims:\n\n"
        f"{summary}"
    )
    result = provider.call_structured(
        system=_KEY_TERMS_SYSTEM,
        user=user_msg,
        schema=KeyTermsResult,
        max_tokens=max_tokens,
    )
    return {
        entry["term"]: entry["definition"]
        for entry in result.get("terms", [])
    }


# ---------------------------------------------------------------------------
# Suggest debate sides
# ---------------------------------------------------------------------------

_SIDES_SYSTEM = textwrap.dedent("""\
    You are a debate strategist.  Given a list of claims from a document,
    your job is to suggest how a structured debate should be set up:

    1. **Proponent claims** -- which claims form the core thesis that a
       Proponent should defend?  Include both the main thesis and the
       most important supporting claims.

    2. **Attack angles** -- what lines of critique should a Skeptic pursue?
       Group related targets together under a descriptive label.
       Consider angles such as:
       - Formal consistency (logical contradictions)
       - Falsifiability / empirical testability
       - Definitional circularity
       - Missing evidence or unjustified leaps
       - Over-generalisation
       - Alternative explanations

    Return a JSON object matching the provided schema.
""")


def suggest_sides(
    claims: list[dict],
    provider: "BaseProvider",
    *,
    max_tokens: int = 8000,
) -> dict:
    """Suggest Proponent claims and Skeptic attack angles for a debate.

    Returns::

        {
            "proponent_claims": ["C1", "C2", ...],
            "attack_angles": [
                {"name": "...", "targets": ["C3"], "description": "..."},
                ...
            ]
        }
    """
    summary = _claims_summary(claims)
    user_msg = (
        "Based on the following claims, suggest which claims a Proponent "
        "should defend and what attack angles a Skeptic should use:\n\n"
        f"{summary}"
    )
    result = provider.call_structured(
        system=_SIDES_SYSTEM,
        user=user_msg,
        schema=SidesResult,
        max_tokens=max_tokens,
    )
    return {
        "proponent_claims": result.get("proponent_claims", []),
        "attack_angles": result.get("attack_angles", []),
    }


# ---------------------------------------------------------------------------
# Claim consolidation -- group granular claims into core theses
# ---------------------------------------------------------------------------

_CONSOLIDATION_SYSTEM = textwrap.dedent("""\
    You are an expert at synthesising complex arguments.  Given a large set
    of granular claims extracted from a document, group them into 5-10 CORE
    THESES.

    Each thesis should:
    1. Be a single coherent assertion that several claims support or elaborate.
    2. List which original claim IDs belong under it (sub_claims).
    3. Identify the dominant intellectual category (structural, empirical,
       ontological, epistemological, normative, methodological, definitional,
       or another appropriate label).
    4. List the key terms and notation used by the original claims in this
       cluster (key_notation).
    5. Include the single most representative quote or paraphrase from the
       sub-claims.

    Rules:
    - Every claim ID must appear in exactly one thesis's sub_claims.
    - Aim for 5-10 theses.  Fewer than 5 means you are over-lumping;
      more than 10 means you are not consolidating enough.
    - Thesis statements should be precise enough to be debatable.
    - Use the author's own terminology in the thesis statement.

    Return JSON matching the provided schema.
""")


def consolidate_claims(
    claims: list[dict],
    provider: "BaseProvider",
    *,
    max_tokens: int = 8000,
) -> list[dict]:
    """Group granular claims into 5-10 core theses with sub-claims.

    Returns list of::

        {
            "id": "T1",
            "thesis": "...",
            "sub_claims": ["C1", "C3", "C12"],
            "category": "structural",
            "key_notation": ["G", "V", "E"],
            "quote": "best supporting quote"
        }
    """
    summary = _claims_summary(claims)
    user_msg = (
        f"Here are {len(claims)} claims extracted from a document.  "
        "Consolidate them into 5-10 core theses.\n\n"
        f"{summary}"
    )
    try:
        result = provider.call_structured(
            system=_CONSOLIDATION_SYSTEM,
            user=user_msg,
            schema=ConsolidationResult,
            max_tokens=max_tokens,
        )
        theses = result.get("theses", [])
        if not theses:
            logger.warning("Consolidation returned empty theses; skipping")
            return []
        logger.info(
            "Consolidated %d claims into %d theses", len(claims), len(theses)
        )
        return theses
    except Exception as exc:
        logger.warning("Claim consolidation failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# Build privileged context for asymmetric information
# ---------------------------------------------------------------------------

_PRIVILEGED_CONTEXT_SYSTEM = textwrap.dedent("""\
    You are building asymmetric information packages for a structured
    adversarial debate.  You will receive:
    - A list of consolidated claims/theses from a theory
    - Identified internal contradictions
    - A glossary of key terms
    - Summaries of reference sources, each classified as
      "supports_theory", "counter_evidence", or "neutral_reference"

    Your task: produce THREE privileged context blocks.

    1. SKEPTIC context: Arm the Skeptic with the strongest possible
       ammunition.  Include:
       - Specific contradiction details with the exact terminology
       - Key objection patterns from the counter-evidence sources
       - Precise language the Skeptic can use to pin down evasions
       - Questions that expose the weakest links
       Do NOT include the theory's supporting arguments (the Skeptic
       should discover the theory's strengths in real-time).

    2. PROPONENT context: Give the Proponent ONLY the theory itself --
       its own framework, notation, and internal logic.  Do NOT give
       the Proponent any counter-evidence or contradiction details.
       The Proponent should defend the theory on its own merits and
       discover objections in real-time.

    3. NEUTRAL context: Give neutral agents (Steelman, Generalist)
       everything -- contradictions, counter-evidence, supporting
       evidence, and key terms.  They need full information to
       referee fairly.

    Use the theory's own terminology throughout.  Be specific, not
    generic.  Reference claim IDs and term names.

    Return a JSON object with keys "skeptic", "proponent", "neutral",
    each containing a multi-paragraph text block.
""")



def build_privileged_context(
    claims: list[dict],
    contradictions: list[dict],
    key_terms: dict[str, str],
    sources: list[str] | None = None,
    provider: "BaseProvider | None" = None,
    *,
    source_classifications: dict[str, list[str]] | None = None,
    counter_thesis: str | None = None,
) -> dict[str, str]:
    """Build asymmetric privileged context for each debate side.

    - Skeptic gets: contradiction details, counter-evidence sources,
      key objection patterns
    - Proponent gets: only the theory itself (no counter-evidence)
    - Neutral agents get: everything

    Parameters
    ----------
    claims:
        Extracted claims.
    contradictions:
        Identified contradictions.
    key_terms:
        Glossary of key terms.
    sources:
        Paths to source files (optional).
    provider:
        LLM provider for generating context.  If None, builds a
        simple rule-based context from the raw data.
    source_classifications:
        Output of ``classify_sources()`` (optional).
    counter_thesis:
        The main counter-thesis, if available.

    Returns
    -------
    dict[str, str]
        Mapping of side label to privileged context text.
        Keys: "Skeptic", "Proponent", "Neutral".
    """
    if provider is None:
        # Simple rule-based fallback
        return _build_privileged_context_simple(
            claims, contradictions, key_terms, counter_thesis,
        )

    # Read source summaries for classified sources
    source_summaries: dict[str, list[str]] = {
        "counter_evidence": [],
        "supports_theory": [],
        "neutral_reference": [],
    }

    if sources and source_classifications:
        for category, paths in source_classifications.items():
            for path in paths:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        text = f.read(2000)
                    source_summaries[category].append(
                        f"[{path}]\n{text[:1000]}"
                    )
                except Exception as exc:
                    logger.warning("Could not read source %s: %s", path, exc)

    claims_text = _claims_summary(claims[:30])
    contra_text = json.dumps(contradictions, indent=2, default=str)
    terms_text = json.dumps(key_terms, indent=2, default=str)
    sources_text = json.dumps(
        {k: [s[:500] for s in v] for k, v in source_summaries.items()},
        indent=2,
        default=str,
    )

    counter_thesis_text = ""
    if counter_thesis:
        counter_thesis_text = f"\nCOUNTER-THESIS:\n{counter_thesis}\n"

    user_msg = textwrap.dedent(f"""\
        CLAIMS:
        {claims_text}

        CONTRADICTIONS:
        {contra_text}

        KEY TERMS:
        {terms_text}

        SOURCE SUMMARIES (by classification):
        {sources_text}
        {counter_thesis_text}
        Build the three privileged context blocks.
    """)

    try:
        result = provider.call_structured(
            system=_PRIVILEGED_CONTEXT_SYSTEM,
            user=user_msg,
            schema=PrivilegedContextResult,
            max_tokens=6000,
        )
        return {
            "Skeptic": result.get("skeptic", ""),
            "Proponent": result.get("proponent", ""),
            "Neutral": result.get("neutral", ""),
        }
    except Exception as exc:
        logger.warning("Privileged context generation failed: %s", exc)
        return _build_privileged_context_simple(
            claims, contradictions, key_terms, counter_thesis,
        )


def _build_privileged_context_simple(
    claims: list[dict],
    contradictions: list[dict],
    key_terms: dict[str, str],
    counter_thesis: str | None = None,
) -> dict[str, str]:
    """Rule-based fallback for privileged context."""
    # Skeptic: contradictions + counter-thesis
    skeptic_parts = ["PRIVILEGED CONTEXT (only Skeptic sees this):\n"]
    if counter_thesis:
        skeptic_parts.append(f"Counter-thesis: {counter_thesis}\n")
    if contradictions:
        skeptic_parts.append("Identified contradictions to press:\n")
        for c in contradictions:
            skeptic_parts.append(
                f"  - {c['claim_a']} vs {c['claim_b']} [{c.get('severity', '?')}]: "
                f"{c['contradiction']}\n"
            )

    # Proponent: just the theory's key terms
    proponent_parts = ["PRIVILEGED CONTEXT (only Proponent sees this):\n"]
    proponent_parts.append("Key terms in your framework:\n")
    for term, defn in key_terms.items():
        proponent_parts.append(f"  - {term}: {defn}\n")

    # Neutral: everything
    neutral_parts = ["PRIVILEGED CONTEXT (all information):\n"]
    if counter_thesis:
        neutral_parts.append(f"Counter-thesis: {counter_thesis}\n")
    if contradictions:
        neutral_parts.append("Contradictions:\n")
        for c in contradictions:
            neutral_parts.append(
                f"  - {c['claim_a']} vs {c['claim_b']}: {c['contradiction']}\n"
            )
    neutral_parts.append("Key terms:\n")
    for term, defn in key_terms.items():
        neutral_parts.append(f"  - {term}: {defn}\n")

    return {
        "Skeptic": "".join(skeptic_parts),
        "Proponent": "".join(proponent_parts),
        "Neutral": "".join(neutral_parts),
    }
