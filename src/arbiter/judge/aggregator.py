"""Score aggregation and spread flagging for the judge panel."""

from __future__ import annotations

import statistics


def aggregate(
    verdicts: dict[str, dict],
    criteria_names: list[str],
    sides: list[str],
    spread_threshold: int = 3,
) -> dict:
    """Aggregate multiple judge verdicts into a panel result.

    Parameters
    ----------
    verdicts:
        ``{judge_name: verdict_dict}`` where each verdict_dict has at
        least ``scores`` (nested by side then criterion) and ``verdict``.
    criteria_names:
        List of criterion id strings (e.g. ``["R1", "R2"]``).
    sides:
        Side names (e.g. ``["Proponent", "Skeptic"]``).
    spread_threshold:
        Flag a criterion as low-confidence when the spread (max - min)
        across judges exceeds this value.

    Returns
    -------
    dict with keys: per_judge, criterion_means, criterion_spreads,
    low_confidence_flags, verdict_counts, panel_verdict.
    """
    agg: dict = {
        "per_judge": verdicts,
        "criterion_means": {},
        "criterion_spreads": {},
        "low_confidence_flags": [],
        "verdict_counts": {},
        "panel_verdict": None,
    }

    fields = criteria_names + ["total"]

    for side in sides:
        agg["criterion_means"][side] = {}
        agg["criterion_spreads"][side] = {}
        for f in fields:
            vals = [v["scores"][side][f] for v in verdicts.values()]
            agg["criterion_means"][side][f] = round(statistics.mean(vals), 2)
            spread = max(vals) - min(vals)
            agg["criterion_spreads"][side][f] = spread
            if f != "total" and spread > spread_threshold:
                agg["low_confidence_flags"].append(
                    f"{side}.{f}: spread={spread} (vals={vals})"
                )

    # Majority vote on verdict
    counts: dict[str, int] = {}
    for v in verdicts.values():
        counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
    agg["verdict_counts"] = counts

    # Determine panel verdict: majority vote wins; on tie, use mean total scores.
    max_votes = max(counts.values())
    leaders = [side for side, c in counts.items() if c == max_votes]
    if len(leaders) == 1:
        agg["panel_verdict"] = leaders[0]
    else:
        # Tie in votes — break by higher mean total score
        score_leaders = [
            s for s in leaders if s in agg["criterion_means"]
        ]
        if score_leaders:
            agg["panel_verdict"] = max(
                score_leaders,
                key=lambda s: agg["criterion_means"][s].get("total", 0),
            )
        else:
            # Fallback (e.g. "Tied" label not in sides) — pick first
            agg["panel_verdict"] = leaders[0]

    return agg
