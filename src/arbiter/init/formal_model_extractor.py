"""Extract formal model structure from extracted claims.

Identifies assumptions, propositions, equations, and policies — the
structured inputs that the Z3 verification suite needs to generate
proof checks, sensitivity analysis, boundary conditions, and policy
verification.

Runs after claim extraction (Step 2) and before contradiction
detection (Step 3). Only runs when the paper has formal claims
(``is_formal`` flag on at least some claims).
"""

from __future__ import annotations

import json
import logging
import textwrap
from typing import TYPE_CHECKING

from arbiter.config import TokenBudgets
from arbiter.schemas import FormalModelResult

if TYPE_CHECKING:
    from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)
_B = TokenBudgets()


_SYSTEM = textwrap.dedent("""\
    You are an expert at identifying formal mathematical structure in academic
    papers. Given a list of extracted claims (some flagged as formal), identify
    the paper's assumptions, propositions, model equations, and policy claims.

    RULES:

    1. ASSUMPTIONS — premises the paper states, takes for granted, or requires
       for its results to hold. Include:
       - Explicit assumptions ("We assume N symmetric firms")
       - Implicit assumptions revealed by the model structure
       - Parameter constraints ("ℓ > 0", "η ∈ [0,1]")
       - Structural assumptions ("The production function is CES")
       Each gets an id (A1, A2, ...), natural language text, formal_expression
       (the math if present), claim_ids (which extracted claims it maps to),
       and z3_hint (what Z3 type to use: "Real inequality", "Bool",
       "ForAll", "Int constraint", etc.).

    2. PROPOSITIONS — results the paper claims to prove or demonstrate.
       Include results labeled "Proposition", "Theorem", "Lemma", "Corollary",
       "Result", or any claim presented as a logical consequence of the
       assumptions. Each gets an id (P1, P2, ...), the assumes list (which
       assumption IDs it depends on), and proof_sketch (brief description of
       HOW the paper argues for it).

    3. MODEL EQUATIONS — the mathematical functions and relationships.
       Include demand functions, utility functions, cost functions, equilibrium
       conditions, transition functions, probability distributions, or any
       named equation. Each gets z3_type_hint for the variables it uses.

    4. POLICIES — normative recommendations with claimed effects.
       Include taxes, subsidies, regulations, interventions, design choices,
       or any "should" claim backed by the model. Note the mechanism (how
       it enters the model) and which assumptions it depends on.

    5. PARAMETER NAMES — list all named parameters (N, φ, η, α, etc.)

    IMPORTANT GUIDELINES:

    - ONLY extract structure that is ACTUALLY present in the paper's claims.
      Do NOT invent equations, assumptions, or propositions.
    - claim_ids MUST reference actual claim IDs from the input.
    - For z3_hint, suggest:
      - "Real inequality" for continuous quantities and comparisons
      - "Bool" for binary conditions (holds/doesn't hold)
      - "Int constraint" for integer quantities (number of firms, etc.)
      - "ForAll" for universal claims ("for all N > 1, ...")
      - "Exists" for existential claims ("there exists τ such that ...")
      - "Optimize" for optimization problems (maximize profit, minimize cost)
      - "not_encodable" for claims that CANNOT be expressed in SMT
        (probability distributions, differential equations, Turing-computability,
        subjective experience, metaphysical identity claims)

    - For papers mixing formal and non-formal content (e.g. a theory using
      graph notation + metaphysical claims about consciousness):
      - Extract the formal mathematical parts as assumptions/propositions
      - Flag metaphysical or non-formal claims with z3_hint: "not_encodable"
      - Do NOT try to formalize what the paper leaves informal

    - For papers with NO formal propositions (pure empirical, narrative,
      or opinion): return empty lists for propositions and equations.
      There may still be implicit assumptions worth extracting.

    Return STRICT JSON matching the provided schema.
""")


def extract_formal_model(
    claims: list[dict],
    source_text: str | None,
    provider: "BaseProvider",
    *,
    max_tokens: int = _B.xl,
) -> dict:
    """Use the LLM to extract formal model structure from claims.

    Parameters
    ----------
    claims:
        Output of ``pdf_reader.extract_claims``.
    source_text:
        Original document text (optional, for additional context).
    provider:
        An Arbiter provider for LLM calls.

    Returns
    -------
    dict matching FormalModelResult schema, or empty structure if
    no formal content is found.
    """
    # Only include formal and structural claims for context efficiency
    formal_claims = [c for c in claims if c.get("is_formal") or c.get("category") in ("structural", "logical")]
    all_claims_brief = [
        {"id": c["id"], "claim": c["claim"][:200], "category": c.get("category", ""), "is_formal": c.get("is_formal", False)}
        for c in claims[:50]  # cap for context size
    ]

    claims_json = json.dumps(all_claims_brief, indent=2, default=str)
    formal_json = json.dumps(
        [{"id": c["id"], "claim": c["claim"], "category": c.get("category", ""), "section": c.get("section", "")}
         for c in formal_claims[:30]],
        indent=2, default=str,
    )

    user = textwrap.dedent(f"""\
        EXTRACTED CLAIMS (all, brief):
        {claims_json}

        FORMAL CLAIMS (detailed):
        {formal_json}

        Extract the formal model structure: assumptions, propositions,
        model equations, policy claims, and parameter names.
    """)

    try:
        result = provider.call_structured(
            system=_SYSTEM,
            user=user,
            schema=FormalModelResult,
            max_tokens=max_tokens,
        )
    except Exception as exc:
        logger.warning("Formal model extraction failed (returning empty): %s", exc)
        return {
            "assumptions": [],
            "propositions": [],
            "equations": [],
            "policies": [],
            "parameter_names": [],
        }

    # Log summary
    n_a = len(result.get("assumptions", []))
    n_p = len(result.get("propositions", []))
    n_eq = len(result.get("equations", []))
    n_pol = len(result.get("policies", []))
    n_params = len(result.get("parameter_names", []))
    logger.info(
        "Formal model: %d assumptions, %d propositions, %d equations, "
        "%d policies, %d parameters",
        n_a, n_p, n_eq, n_pol, n_params,
    )

    return result
