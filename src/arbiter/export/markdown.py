"""Export debate state to a readable Markdown document."""

from __future__ import annotations

from typing import Any, Dict, List


def export_markdown(state: Dict[str, Any], config_name: str = "") -> str:
    """Render the full debate transcript, ledger, and verdict as Markdown.

    Parameters
    ----------
    state:
        Dict matching :class:`arbiter.state.DebateState` keys.
    config_name:
        Optional label for the debate heading.
    """
    parts: List[str] = []

    # Title
    title = f"Debate: {config_name}" if config_name else "Debate Transcript"
    parts.append(f"# {title}\n")

    # Transcript — grouped by round
    transcript: List[Dict[str, Any]] = state.get("transcript", [])
    rounds: Dict[int, List[Dict[str, Any]]] = {}
    for entry in transcript:
        r = entry.get("round", entry.get("round_idx", 0))
        rounds.setdefault(r, []).append(entry)

    for r_idx in sorted(rounds):
        parts.append(f"## Round {r_idx}\n")
        for entry in rounds[r_idx]:
            agent = entry.get("agent", entry.get("side", "Unknown"))
            text = entry.get("text", entry.get("content", ""))
            parts.append(f"### {agent}\n")
            parts.append(f"{text}\n")

    # Argument ledger
    ledger: List[Dict[str, Any]] = state.get("ledger", [])
    if ledger:
        parts.append("## Argument Ledger\n")
        parts.append("| ID | By | Against | Claim | Status |")
        parts.append("|----|----|---------|-------|--------|")
        for h in ledger:
            claim = (h.get("claim") or "").replace("\n", " ").strip()
            # Truncate very long claims for table readability
            if len(claim) > 120:
                claim = claim[:117] + "..."
            parts.append(
                f"| {h.get('id', '')} "
                f"| {h.get('by', '')} "
                f"| {h.get('against', '')} "
                f"| {claim} "
                f"| {h.get('status', '')} |"
            )
        parts.append("")

    # Formal verdict
    verdict = state.get("formal_verdict", "")
    if verdict:
        parts.append("## Formal Verdict\n")
        parts.append(f"{verdict}\n")

    return "\n".join(parts)
