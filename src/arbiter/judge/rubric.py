"""Dynamic Pydantic model generation from rubric config."""

from __future__ import annotations

from typing import List

from pydantic import Field, create_model

from arbiter.config import RubricCriterion


def build_verdict_models(
    criteria: list[RubricCriterion],
    sides: list[str],
    verdict_options: list[str],
) -> tuple[type, type]:
    """Build (SideScores, Verdict) Pydantic models from config.

    Parameters
    ----------
    criteria:
        Rubric criteria; each becomes an int field on SideScores.
    sides:
        Side names (e.g. ["Proponent", "Skeptic"]); each becomes a
        SideScores field on the inner Scores model.
    verdict_options:
        Valid verdict strings (e.g. ["Proponent", "Skeptic", "Tied"]).

    Returns
    -------
    (SideScores, Verdict) -- both are Pydantic BaseModel subclasses.
    """

    # -- SideScores: one int field per criterion + total ----------------
    max_total = sum(c.max_score for c in criteria)
    side_fields: dict = {}
    for c in criteria:
        side_fields[c.id] = (
            int,
            Field(ge=c.min_score, le=c.max_score, description=c.description),
        )
    side_fields["total"] = (
        int,
        Field(ge=0, le=max_total, description="Sum of all criterion scores"),
    )

    SideScores = create_model("SideScores", **side_fields)

    # -- Scores: one SideScores field per side --------------------------
    scores_fields: dict = {}
    for side in sides:
        scores_fields[side] = (SideScores, ...)

    Scores = create_model("Scores", **scores_fields)

    # -- Verdict --------------------------------------------------------
    verdict_desc = f"One of: {', '.join(repr(v) for v in verdict_options)}"
    Verdict = create_model(
        "Verdict",
        scores=(Scores, ...),
        key_landed_hits=(List[str], Field(description="Key arguments that landed")),
        key_dodged_questions=(List[str], Field(description="Key questions that were dodged")),
        verdict=(str, Field(description=verdict_desc)),
        verdict_reasoning=(str, Field(description="Brief reasoning for the verdict")),
    )

    return SideScores, Verdict


def rubric_description(criteria: list[RubricCriterion]) -> str:
    """Render human-readable rubric text from criteria list."""
    lines = ["Score each criterion (integer):"]
    for c in criteria:
        lines.append(
            f"  {c.id} ({c.name}): {c.description}  [{c.min_score}-{c.max_score}]"
        )
    max_total = sum(c.max_score for c in criteria)
    lines.append(f"total = sum of all criterion scores (0-{max_total}).")
    return "\n".join(lines)
