"""Higher-level claim analysis: contradictions, key terms, debate sides."""

from __future__ import annotations

import json
import logging
import textwrap
from typing import TYPE_CHECKING

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

_CONTRADICTION_SCHEMA = {
    "type": "object",
    "properties": {
        "contradictions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim_a": {
                        "type": "string",
                        "description": "ID of the first claim."
                    },
                    "claim_b": {
                        "type": "string",
                        "description": "ID of the second claim."
                    },
                    "contradiction": {
                        "type": "string",
                        "description": (
                            "A clear explanation of how the two claims "
                            "conflict or create tension."
                        ),
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["fatal", "tension", "ambiguity"],
                        "description": (
                            "How severe the contradiction is: "
                            "'fatal' = logically irreconcilable, "
                            "'tension' = in friction but possibly reconcilable, "
                            "'ambiguity' = apparent conflict due to vague terms."
                        ),
                    },
                    "z3_encodable": {
                        "type": "boolean",
                        "description": (
                            "True if this contradiction can be encoded as a "
                            "Z3/SMT check."
                        ),
                    },
                },
                "required": [
                    "claim_a",
                    "claim_b",
                    "contradiction",
                    "severity",
                    "z3_encodable",
                ],
            },
        }
    },
    "required": ["contradictions"],
}

_CONTRADICTION_SYSTEM = textwrap.dedent("""\
    You are an expert logician and critical analyst.  Given a numbered list
    of claims extracted from a single document, your task is to identify
    ALL potential internal contradictions, tensions, or ambiguities between
    pairs of claims.

    Rules:
    1. Be thorough — check every plausible pair.
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

    Returns a list of contradiction dicts (see ``_CONTRADICTION_SCHEMA``).
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
        schema=_CONTRADICTION_SCHEMA,
        max_tokens=max_tokens,
    )
    return result.get("contradictions", [])


# ---------------------------------------------------------------------------
# Key-term extraction
# ---------------------------------------------------------------------------

_KEY_TERMS_SCHEMA = {
    "type": "object",
    "properties": {
        "terms": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "term": {
                        "type": "string",
                        "description": "The key term or phrase."
                    },
                    "definition": {
                        "type": "string",
                        "description": (
                            "A concise definition as used in the document."
                        ),
                    },
                },
                "required": ["term", "definition"],
            },
        }
    },
    "required": ["terms"],
}

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
        schema=_KEY_TERMS_SCHEMA,
        max_tokens=max_tokens,
    )
    return {
        entry["term"]: entry["definition"]
        for entry in result.get("terms", [])
    }


# ---------------------------------------------------------------------------
# Suggest debate sides
# ---------------------------------------------------------------------------

_SIDES_SCHEMA = {
    "type": "object",
    "properties": {
        "proponent_claims": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "Claim IDs the Proponent should defend — the core "
                "thesis and its critical supporting claims."
            ),
        },
        "attack_angles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Short label for the attack angle."
                    },
                    "targets": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Claim IDs targeted by this angle."
                    },
                    "description": {
                        "type": "string",
                        "description": (
                            "Explanation of the critique and why it is "
                            "worth pursuing."
                        ),
                    },
                },
                "required": ["name", "targets", "description"],
            },
        },
    },
    "required": ["proponent_claims", "attack_angles"],
}

_SIDES_SYSTEM = textwrap.dedent("""\
    You are a debate strategist.  Given a list of claims from a document,
    your job is to suggest how a structured debate should be set up:

    1. **Proponent claims** — which claims form the core thesis that a
       Proponent should defend?  Include both the main thesis and the
       most important supporting claims.

    2. **Attack angles** — what lines of critique should a Skeptic pursue?
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
        schema=_SIDES_SCHEMA,
        max_tokens=max_tokens,
    )
    return {
        "proponent_claims": result.get("proponent_claims", []),
        "attack_angles": result.get("attack_angles", []),
    }
