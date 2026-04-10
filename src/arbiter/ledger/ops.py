"""Ledger operations -- add, resolve, query hits."""

from __future__ import annotations

from typing import List

from arbiter.state import Hit


def add_hit(
    ledger: List[Hit],
    by: str,
    against: str,
    claim: str,
    round_idx: int,
) -> List[Hit]:
    """Append a new open hit to the ledger and return the updated list.

    The hit ID is auto-assigned as ``h{N+1}`` where *N* is the current
    ledger length.
    """
    ledger = list(ledger)  # shallow copy
    next_id = len(ledger) + 1
    ledger.append(
        Hit(
            id=f"h{next_id}",
            by=by,
            against=against,
            claim=claim[:300],
            status="open",
            rebuttal="",
            round_landed=round_idx,
        )
    )
    return ledger


def resolve_hit(
    ledger: List[Hit],
    hit_id: str,
    status: str,
    rebuttal: str = "",
) -> List[Hit]:
    """Mark an existing hit as resolved and return the updated ledger.

    Parameters
    ----------
    hit_id:
        The ``id`` field of the hit to update (e.g. ``"h3"``).
    status:
        One of ``"conceded"``, ``"rebutted"``, ``"dodged"``.
    rebuttal:
        Rebuttal text (truncated to 500 chars).
    """
    ledger = list(ledger)
    for h in ledger:
        if h["id"] == hit_id:
            h["status"] = status  # type: ignore[typeddict-item]
            h["rebuttal"] = rebuttal[:500]
            break
    return ledger


def open_hits(
    ledger: List[Hit],
    against: str | None = None,
) -> List[Hit]:
    """Return all hits with ``status == 'open'``.

    If *against* is given, filter to hits targeting that side/agent.
    """
    result = [h for h in ledger if h["status"] == "open"]
    if against is not None:
        result = [h for h in result if h["against"] == against]
    return result


def ledger_grew(ledger: List[Hit], last_size: int) -> bool:
    """Return True if the ledger has more entries than *last_size*."""
    return len(ledger) > last_size
