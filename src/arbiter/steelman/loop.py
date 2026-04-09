"""Iterated steelman rescue/attack loop."""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)

# ── Prompts ───────────────────────────────────────────────────────────

_STEELMAN_SYSTEM = """\
You are a charitable but rigorous philosopher of science.
Your job is to RESCUE the theory by reformulating it to close known objections.

Your output MUST:
1. Begin with a section "CLAIMS PRESERVED / DROPPED / MODIFIED" that goes
   through each numbered claim one at a time and states explicitly for each
   whether it is PRESERVED (unchanged), DROPPED (removed), or MODIFIED
   (and how).
2. Then give the rescued reformulation as a coherent position.
3. If a prior attack is provided, address that attack DIRECTLY and explain
   how the new rescue closes the objection.
4. Be honest: if a claim cannot be saved, say so and drop it."""

_CRITIC_SYSTEM = """\
You are a strict, unsparing analytic critic. You will be shown a steelmanned
rescue of a theory. Your job is to find the SHARPEST single objection that
the rescued version has NOT actually fixed.

Rules:
- Do not grant the rescue more than it actually proved.
- Focus on load-bearing weaknesses, not stylistic complaints.
- One paragraph maximum."""

_STABILIZATION_SYSTEM = "You are a strict judge. Output only JSON."


# ── Helpers ───────────────────────────────────────────────────────────


def _steelman_call(
    provider: "BaseProvider",
    theory_summary: str,
    prior_version: str | None,
    prior_attack: str | None,
) -> str:
    parts = [f"THEORY TO RESCUE:\n{theory_summary}"]
    if prior_version is not None:
        parts.append(f"\nYOUR PREVIOUS RESCUE:\n{prior_version}")
    if prior_attack is not None:
        parts.append(
            f"\nCRITIC'S ATTACK ON THAT RESCUE (address this directly):\n{prior_attack}"
        )
    parts.append("\nProduce the (next) rescue now, following the required structure.")
    user_msg = "\n".join(parts)
    return provider.call(system=_STEELMAN_SYSTEM, user=user_msg, max_tokens=12_000)


def _critic_call(provider: "BaseProvider", rescue: str) -> str:
    user_msg = (
        f"RESCUED VERSION:\n{rescue}\n\nGive your sharpest single objection."
    )
    return provider.call(system=_CRITIC_SYSTEM, user=user_msg, max_tokens=4_000)


def _stabilized(
    provider: "BaseProvider",
    version_a: str,
    version_b: str,
) -> tuple[bool, str]:
    user_msg = (
        "Compare these two rescue versions of a theory. Return JSON "
        '{"stabilized": bool, "reason": "..."}. Set stabilized=true only if '
        "the load-bearing claims are unchanged and the differences are "
        "stylistic only.\n\n"
        f"VERSION A:\n{version_a}\n\nVERSION B:\n{version_b}"
    )
    raw = provider.call(
        system=_STABILIZATION_SYSTEM, user=user_msg, max_tokens=2_000
    )
    # Strip markdown code fences if present
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        data = json.loads(text)
        return bool(data.get("stabilized", False)), str(data.get("reason", ""))
    except (json.JSONDecodeError, ValueError):
        # Try to find JSON object in the response
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(0))
                return bool(data.get("stabilized", False)), str(
                    data.get("reason", "")
                )
            except (json.JSONDecodeError, ValueError):
                pass
        return False, f"could not parse judge output: {text[:200]}"


# ── Main loop ─────────────────────────────────────────────────────────


def iterated_steelman(
    theory_summary: str,
    steelman_provider: "BaseProvider",
    critic_provider: "BaseProvider",
    judge_provider: "BaseProvider",
    max_iterations: int = 4,
) -> dict:
    """Run the iterated rescue/attack loop.

    Parameters
    ----------
    theory_summary:
        Plain-text description of the theory to rescue.
    steelman_provider:
        Provider for the steelman (rescue) role.
    critic_provider:
        Provider for the critic (attack) role.
    judge_provider:
        Provider for stabilization checking.
    max_iterations:
        Maximum rescue/attack cycles (default 4).

    Returns
    -------
    dict with keys: versions, attacks, iterations, final_version, stabilized.
    """
    versions: list[str] = []
    attacks: list[str] = []
    stabilization_reasons: list[str] = []

    logger.info("[steelman] initial rescue...")
    rescue = _steelman_call(steelman_provider, theory_summary, None, None)
    versions.append(rescue)

    stabilized_flag = False
    for i in range(max_iterations):
        logger.info("[critic] iteration %d...", i + 1)
        attack = _critic_call(critic_provider, rescue)
        attacks.append(attack)

        logger.info("[steelman] re-rescue %d...", i + 1)
        new_rescue = _steelman_call(
            steelman_provider, theory_summary, rescue, attack
        )
        versions.append(new_rescue)

        logger.info("[judge] stabilization check %d...", i + 1)
        is_stable, reason = _stabilized(judge_provider, rescue, new_rescue)
        stabilization_reasons.append(reason)
        if is_stable:
            stabilized_flag = True
            rescue = new_rescue
            break
        rescue = new_rescue

    return {
        "versions": versions,
        "attacks": attacks,
        "stabilization_reasons": stabilization_reasons,
        "iterations": len(versions),
        "final_version": versions[-1],
        "stabilized": stabilized_flag,
    }
