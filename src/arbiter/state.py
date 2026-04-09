"""Core state types for the LangGraph debate engine."""

from __future__ import annotations

from operator import add
from typing import Annotated, Any, Dict, List, Literal, TypedDict


class Hit(TypedDict):
    """A single argument-ledger entry tracking one claim and its resolution."""

    id: str  # h1, h2, ...
    by: str  # agent name
    against: str  # target side or agent
    claim: str  # one-sentence statement
    status: Literal["open", "conceded", "rebutted", "dodged"]
    rebuttal: str  # text of rebuttal if any
    round_landed: int


class DebateState(TypedDict):
    """LangGraph shared state for a debate run."""

    round_idx: int
    transcript: Annotated[List[Dict[str, Any]], add]  # append-only per-turn entries
    ledger: List[Hit]
    last_ledger_size: int
    rounds_without_growth: int
    judge_signals: Dict[str, str]  # per-agent guidance from mid-debate judge
    steelman_versions: List[str]
    formal_verdict: str
    halt: bool
    validity_log: Annotated[List[Dict[str, Any]], add]  # gate audit trail


def initial_state() -> DebateState:
    """Return a fresh initial state for a new debate."""
    return DebateState(
        round_idx=1,
        transcript=[],
        ledger=[],
        last_ledger_size=0,
        rounds_without_growth=0,
        judge_signals={},
        steelman_versions=[],
        formal_verdict="",
        halt=False,
        validity_log=[],
    )
