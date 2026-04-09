"""Export the argument ledger to Argdown markup."""

from __future__ import annotations

from typing import Dict, List


def export_argdown(ledger: List[Dict], sides: List[str]) -> str:
    """Convert a Hit-style ledger to `Argdown <https://argdown.org>`_ markup.

    Each hit becomes a statement ``[hN]: claim text`` grouped under its
    originating side.  Rebuttals are linked as attacking relations (``-``)
    and same-side follow-ups as supporting relations (``+``).

    Parameters
    ----------
    ledger:
        List of dicts with keys ``id``, ``by``, ``against``, ``claim``,
        ``status``, ``rebuttal``, ``round_landed``.
    sides:
        Ordered list of side labels (e.g. ``["Proponent", "Skeptic"]``).
    """
    if not ledger:
        return "// Empty ledger — no arguments recorded.\n"

    # Index hits by id for cross-referencing
    by_id: Dict[str, Dict] = {h["id"]: h for h in ledger}

    # Group hit ids by the *by* field (agent/side)
    groups: Dict[str, List[str]] = {s: [] for s in sides}
    for h in ledger:
        side = h.get("by", "")
        if side not in groups:
            groups[side] = []
        groups[side].append(h["id"])

    lines: List[str] = [
        "===",
        "title: Argument Ledger",
        "===",
        "",
    ]

    for side in list(groups.keys()):
        ids = groups[side]
        if not ids:
            continue
        lines.append(f"// --- {side} ---")
        lines.append("")
        for hid in ids:
            h = by_id[hid]
            status = h.get("status", "open")
            claim = h.get("claim", "").replace("\n", " ").strip()
            lines.append(f"[{hid}]: {claim} #{status}")

            # Find rebuttals *against* this hit (another hit whose
            # rebuttal text is non-empty and targets this claim).
            for other in ledger:
                if other["id"] == hid:
                    continue
                if (
                    other.get("rebuttal")
                    and other.get("against") == h.get("by")
                    and status == "rebutted"
                ):
                    lines.append(f"  - <{other['id']}>: {other['rebuttal'].replace(chr(10), ' ').strip()}")
                elif other.get("by") == h.get("by") and other["id"] != hid:
                    # Same side — supporting relation (only immediate neighbours)
                    pass  # handled at statement level, not duplicated

            lines.append("")

    # Explicit relation section
    lines.append("// --- Relations ---")
    lines.append("")
    for h in ledger:
        status = h.get("status", "open")
        rebuttal_text = (h.get("rebuttal") or "").strip()
        if status == "rebutted" and rebuttal_text:
            # Find the rebutting hit (the one whose claim matches the rebuttal)
            rebutter_id = None
            for other in ledger:
                if other["id"] == h["id"]:
                    continue
                if other.get("by") == h.get("against"):
                    other_claim = (other.get("claim") or "").strip()
                    if other_claim and other_claim in rebuttal_text:
                        rebutter_id = other["id"]
                        break
            if rebutter_id:
                lines.append(f"<{rebutter_id}> - [{h['id']}]")
            else:
                lines.append(f"// [{h['id']}] marked rebutted: {rebuttal_text[:80]}")

    # Same-side support relations
    for side in groups:
        ids = groups[side]
        for i in range(1, len(ids)):
            lines.append(f"[{ids[i]}] + [{ids[i - 1]}]")

    lines.append("")
    return "\n".join(lines)
