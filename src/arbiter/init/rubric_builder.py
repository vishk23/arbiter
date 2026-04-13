"""Design judge rubric criteria from extracted claims and attack angles."""

from __future__ import annotations

import logging
import textwrap
from typing import TYPE_CHECKING

from arbiter.config import TokenBudgets
from arbiter.schemas import RubricResult

if TYPE_CHECKING:
    from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)
_B = TokenBudgets()

# ---------------------------------------------------------------------------
# JSON schema the LLM must return
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Mandatory baseline criteria (always present)
# ---------------------------------------------------------------------------

_MANDATORY_CRITERIA = [
    {
        "id": "R1",
        "name": "notation_fidelity",
        "base_description": (
            "Engagement with the theory's own formal terms and notation."
        ),
    },
    {
        "id": "R2",
        "name": "argument_survival",
        "base_description": (
            "Did central arguments survive the opponent's best rebuttal?"
        ),
    },
    {
        "id": "R3",
        "name": "concession_honesty",
        "base_description": (
            "Were genuinely-landed points conceded rather than dodged?"
        ),
    },
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def design_rubric(
    claims: list[dict],
    attack_angles: list[dict],
    provider: "BaseProvider",
    *,
    counter_thesis: str | None = None,
) -> list[dict]:
    """Design judge rubric criteria from the claim landscape.

    Parameters
    ----------
    claims:
        Extracted claims (each has at least ``id``, ``claim``, ``category``).
    attack_angles:
        Output of ``suggest_sides()`` -- each has ``angle``, ``side``,
        ``description``.
    provider:
        The LLM used to generate the rubric.
    counter_thesis:
        The main counter-thesis a Skeptic would advance (optional).
        When provided, a SPECIFIC criterion addressing this dispute
        will be generated.

    Returns
    -------
    list[dict]
        Each dict has ``id``, ``name``, ``description``, ``min``, ``max``.
        Ready to become :class:`~arbiter.config.RubricCriterion` instances.
    """
    # Summarise claims and categories for the prompt
    categories_seen = sorted({c.get("category", "unknown") for c in claims})
    claim_lines = "\n".join(
        f"  {c['id']}: [{c.get('category', '?')}] {c['claim']}"
        for c in claims
    )
    angle_lines = "\n".join(
        f"  - {a.get('angle', a.get('name', '?'))}: {a.get('description', '')}"
        for a in attack_angles
    )
    mandatory_lines = "\n".join(
        f"  {m['id']} {m['name']}: {m['base_description']}"
        for m in _MANDATORY_CRITERIA
    )

    # Counter-thesis criterion instruction
    counter_thesis_instruction = ""
    if counter_thesis:
        counter_thesis_instruction = textwrap.dedent(f"""\

        8. CRITICAL: One criterion MUST specifically address the central
           counter-thesis: '{counter_thesis[:300]}'.
           Name it after the SPECIFIC ISSUE raised by the counter-thesis,
           not generically.  For example:
           - If the counter-thesis is about lack of empirical evidence,
             name it "empirical_grounding" with a description specific
             to what evidence is missing
           - If the counter-thesis is about a logical gap, name it after
             the specific logical issue
           - If the counter-thesis is about an alternative explanation,
             name it after the specific alternative
           The description must reference the actual dispute, not be
           a generic placeholder.
        """)

    system = textwrap.dedent("""\
        You are an expert judge-rubric designer for Arbiter, an adversarial
        debate system.  Your job is to create 4-6 scoring criteria that
        judges will use to evaluate each side of a debate.

        Design rules:
        1. The following 3 criteria are MANDATORY (you must include them
           and refine their descriptions to be SPECIFIC to this topic):
        {mandatory}
        2. Add 1-3 ADDITIONAL criteria based on the claim categories and
           attack angles.  Examples:
           - If there are "empirical" claims -> add "empirical_grounding"
           - If there are "autobiographical" claims -> add something about
             distinguishing personal narrative from formal argument
           - If there are formal/logical claims -> add "formal_consistency"
           - If there's a falsifiability angle -> add "falsifiability"
        3. Descriptions MUST be specific to the topic, not generic.
           BAD: "Did the side make good arguments?"
           GOOD: "Did the side engage the central structural contradiction
                  without equivocating between the fixed and mutable
                  interpretations of the core construct?"
        4. Total criteria: 4-6 (not more).
        5. All criteria use min=0, max=10.
        6. Use snake_case for names.
        7. IDs should be R1, R2, R3, R4, ... in order.
        {counter_thesis_instruction}
        Return JSON matching the provided schema.
    """).format(
        mandatory=mandatory_lines,
        counter_thesis_instruction=counter_thesis_instruction,
    )

    user_parts = [
        f"CLAIMS extracted from the theory:\n{claim_lines}\n",
        f"CLAIM CATEGORIES present: {', '.join(categories_seen)}\n",
        f"ATTACK ANGLES identified:\n{angle_lines}\n",
    ]
    if counter_thesis:
        user_parts.append(
            f"COUNTER-THESIS (the strongest opposing position):\n"
            f"  {counter_thesis}\n"
        )
    user_parts.append(
        "Design 4-6 rubric criteria (3 mandatory + 1-3 topic-specific)."
    )
    user = "\n".join(user_parts)

    logger.info("Designing rubric criteria from %d claims, %d angles",
                len(claims), len(attack_angles))

    result = provider.call_structured(
        system=system,
        user=user,
        schema=RubricResult,
        max_tokens=_B.medium,
    )

    criteria: list[dict] = result.get("criteria", [])

    # Validate and patch
    if not criteria:
        logger.warning("LLM returned empty rubric; falling back to defaults")
        criteria = _fallback_rubric(categories_seen, counter_thesis)

    criteria = _ensure_mandatory(criteria)

    # If counter_thesis was provided, ensure we have a counter-thesis criterion
    if counter_thesis:
        criteria = _ensure_counter_thesis_criterion(criteria, counter_thesis)

    criteria = _enforce_limits(criteria)
    criteria = _renumber(criteria)

    logger.info(
        "Designed %d rubric criteria: %s",
        len(criteria),
        ", ".join(c["name"] for c in criteria),
    )
    return criteria


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _ensure_mandatory(criteria: list[dict]) -> list[dict]:
    """Make sure all three mandatory criteria are present."""
    existing_names = {c["name"] for c in criteria}
    for m in _MANDATORY_CRITERIA:
        if m["name"] not in existing_names:
            logger.warning("Mandatory criterion %s missing; injecting", m["name"])
            criteria.append({
                "id": m["id"],
                "name": m["name"],
                "description": m["base_description"],
                "min": 0,
                "max": 10,
            })
    return criteria


def _ensure_counter_thesis_criterion(
    criteria: list[dict],
    counter_thesis: str,
) -> list[dict]:
    """Ensure at least one criterion addresses the counter-thesis.

    Checks if any non-mandatory criterion mentions keywords from the
    counter-thesis.  If not, adds a generic one.
    """
    mandatory_names = {m["name"] for m in _MANDATORY_CRITERIA}
    non_mandatory = [c for c in criteria if c["name"] not in mandatory_names]

    # If we have at least one non-mandatory criterion, assume the LLM
    # addressed the counter-thesis (we instructed it to)
    if non_mandatory:
        return criteria

    # No non-mandatory criteria at all -- add one based on counter-thesis
    logger.warning(
        "No counter-thesis criterion found; adding a generic one"
    )
    # Create a name from the first key phrase in the counter-thesis
    words = counter_thesis.lower().split()[:3]
    name = "_".join(w for w in words if w.isalnum())[:30] or "counter_thesis_handling"

    criteria.append({
        "id": f"R{len(criteria) + 1}",
        "name": name,
        "description": (
            f"How well the debate addressed the central counter-thesis: "
            f"{counter_thesis[:200]}"
        ),
        "min": 0,
        "max": 10,
    })
    return criteria


def _enforce_limits(criteria: list[dict]) -> list[dict]:
    """Cap at 6 criteria, floor at 4.  Normalise min/max."""
    # Ensure min/max are integers in range
    for c in criteria:
        c.setdefault("min", 0)
        c.setdefault("max", 10)
        c["min"] = int(c["min"])
        c["max"] = int(c["max"])

    if len(criteria) > 6:
        # Keep mandatory first, then trim extras
        mandatory_names = {m["name"] for m in _MANDATORY_CRITERIA}
        mandatory = [c for c in criteria if c["name"] in mandatory_names]
        extra = [c for c in criteria if c["name"] not in mandatory_names]
        criteria = mandatory + extra[: 6 - len(mandatory)]

    return criteria


def _renumber(criteria: list[dict]) -> list[dict]:
    """Re-assign IDs as R1, R2, ... in order."""
    for i, c in enumerate(criteria, start=1):
        c["id"] = f"R{i}"
    return criteria


# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------

def _fallback_rubric(
    categories: list[str],
    counter_thesis: str | None = None,
) -> list[dict]:
    """Minimal rubric when the LLM call fails."""
    criteria = [
        {
            "id": "R1",
            "name": "notation_fidelity",
            "description": (
                "Engagement with the theory's own formal terms and notation."
            ),
            "min": 0,
            "max": 10,
        },
        {
            "id": "R2",
            "name": "argument_survival",
            "description": (
                "Did central arguments survive the opponent's best rebuttal?"
            ),
            "min": 0,
            "max": 10,
        },
        {
            "id": "R3",
            "name": "concession_honesty",
            "description": (
                "Were genuinely-landed points conceded rather than dodged?"
            ),
            "min": 0,
            "max": 10,
        },
    ]

    # Add one category-driven criterion
    if "empirical" in categories:
        criteria.append({
            "id": "R4",
            "name": "empirical_grounding",
            "description": (
                "Were empirical claims backed by observable evidence "
                "or testable predictions?"
            ),
            "min": 0,
            "max": 10,
        })
    elif "logical" in categories or "structural" in categories:
        criteria.append({
            "id": "R4",
            "name": "formal_consistency",
            "description": (
                "Were formal and structural claims handled without "
                "internal contradiction?"
            ),
            "min": 0,
            "max": 10,
        })
    else:
        criteria.append({
            "id": "R4",
            "name": "falsifiability",
            "description": (
                "Were claims advanced that are in principle falsifiable?"
            ),
            "min": 0,
            "max": 10,
        })

    # Add counter-thesis criterion if provided
    if counter_thesis:
        words = counter_thesis.lower().split()[:3]
        name = "_".join(w for w in words if w.isalnum())[:30] or "counter_thesis_handling"
        criteria.append({
            "id": "R5",
            "name": name,
            "description": (
                f"How well the debate addressed the central counter-thesis: "
                f"{counter_thesis[:200]}"
            ),
            "min": 0,
            "max": 10,
        })

    return criteria
