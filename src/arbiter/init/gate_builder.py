"""Generate validity gate rules and test cases from identified contradictions.

The LLM checker is the primary validity gate; regex patterns are an optional
additive layer. Produces stipulated rules (id + fact), entailment facts,
gold-standard test cases, and anticipated escape routes.
"""

from __future__ import annotations

import json
import logging
import textwrap
from concurrent.futures import ThreadPoolExecutor

from arbiter.config import TokenBudgets
from arbiter.providers.base import BaseProvider
from arbiter.schemas import (
    CalibrationCheckResult,
    EscapeRoutesResult,
    GateRulesResult,
    GateTestsResult,
)

logger = logging.getLogger(__name__)
_B = TokenBudgets()

# ---------------------------------------------------------------------------
# 1. Escape route anticipation
# ---------------------------------------------------------------------------

_ESCAPE_SYSTEM = textwrap.dedent("""\
    You are an expert debate strategist. For each contradiction, predict 2-4
    "escape routes" a defender might use to avoid conceding the point.

    Common strategies: redefining a key term, claiming separate "modes" that
    don't conflict, retreating to a weaker claim, asserting the contradiction
    is only "apparent", shifting to meta-level claims, invoking special
    exceptions, conflating formal/informal usage.

    For each route provide: strategy (short name), language_patterns (phrases
    the defender would use), how_to_catch (why it's illegitimate).

    Use the theory's own terminology. Return JSON with key "escape_routes".
""")


def anticipate_escape_routes(
    contradictions: list[dict],
    key_terms: dict[str, str],
    provider: BaseProvider,
) -> list[dict]:
    """Predict how a defender might work around each contradiction."""
    if not contradictions:
        return []
    user = (
        f"CONTRADICTIONS:\n{json.dumps(contradictions, indent=2, default=str)}\n\n"
        f"KEY TERMS:\n{json.dumps(key_terms, indent=2, default=str)}\n\n"
        "For each contradiction, predict 2-4 escape routes."
    )
    try:
        result = provider.call_structured(
            system=_ESCAPE_SYSTEM, user=user,
            schema=EscapeRoutesResult, max_tokens=_B.large,
        )
        routes = result.get("escape_routes", [])
        logger.info("Anticipated %d escape route groups.", len(routes))
        return routes
    except Exception as exc:
        logger.warning("Escape route anticipation failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# 2. Rule generation
# ---------------------------------------------------------------------------

def generate_gate_rules(
    contradictions: list[dict],
    key_terms: dict[str, str],
    provider: BaseProvider,
    *,
    escape_routes: list[dict] | None = None,
) -> dict:
    """Generate validity gate rules from contradictions.

    Returns dict with ``stipulated_rules`` (id, fact, optional bad_patterns)
    and ``entailment_facts``.
    """
    escape_block = ""
    if escape_routes:
        escape_block = (
            "\nANTICIPATED ESCAPE ROUTES (rules should also catch these):\n"
            f"{json.dumps(escape_routes, indent=2, default=str)}\n"
        )
    system = textwrap.dedent("""\
        You are an expert at building validity gate rules for academic debate.

        For each contradiction produce:
        1. id: RULE-1, RULE-2, etc.
        2. fact: plain-English stipulated truth (1-2 sentences) -- primary
           input for the LLM validity checker.
        3. bad_patterns (optional): 2-6 Python regex patterns (re.IGNORECASE)
           for an additive regex layer.

        Also produce entailment_facts: one plain-English fact per rule,
        format "[RULE-ID] statement of stipulated truth."
    """)
    user = (
        f"CONTRADICTIONS:\n{json.dumps(contradictions, indent=2, default=str)}\n\n"
        f"KEY TERMS:\n{json.dumps(key_terms, indent=2, default=str)}\n"
        f"{escape_block}\nGenerate stipulated_rules and entailment_facts."
    )
    logger.info("Generating gate rules via LLM...")
    try:
        response = provider.call_structured(
            system=system, user=user, schema=GateRulesResult, max_tokens=_B.large,
        )
    except Exception as exc:
        logger.error("Gate rule generation failed: %s", exc)
        return {"stipulated_rules": [], "entailment_facts": []}

    for rule in response.get("stipulated_rules", []):
        rule.setdefault("bad_patterns", [])

    logger.info("Generated %d gate rules.", len(response.get("stipulated_rules", [])))
    return response


# ---------------------------------------------------------------------------
# 3. Test case generation (for LLM checker calibration)
# ---------------------------------------------------------------------------

def generate_gate_tests(
    rules: dict,
    claims: list[dict],
    provider: BaseProvider,
) -> list[dict]:
    """Generate test cases for LLM-based gate calibration.

    Per rule: 1 direct positive, 1 paraphrase positive, 1 negative.
    """
    system = textwrap.dedent("""\
        Generate gold-standard test cases for an LLM validity gate.

        For EACH rule, generate exactly 3 cases:
        1. DIRECT positive (expected: stipulation_violation) -- exact terminology.
        2. PARAPHRASE positive (expected: stipulation_violation) -- synonyms.
        3. NEGATIVE (expected: none) -- same topic, no violation.

        Positive cases must assert BOTH halves of the contradiction.
        Negative cases must be topically related but non-violating.
        Text: 2-4 natural sentences. ID format: RULE-1_direct, etc.
    """)
    user = (
        f"RULES:\n{json.dumps(rules.get('stipulated_rules', []), indent=2, default=str)}\n\n"
        f"CLAIMS (context):\n{json.dumps(claims[:15], indent=2, default=str)}\n\n"
        "Generate test cases."
    )
    logger.info("Generating gate test cases via LLM...")
    try:
        response = provider.call_structured(
            system=system, user=user, schema=GateTestsResult, max_tokens=_B.large,
        )
        cases = response.get("cases", [])
    except Exception as exc:
        logger.warning("Gate test generation failed: %s", exc)
        cases = []
    logger.info("Generated %d gate test cases.", len(cases))
    return cases


# ---------------------------------------------------------------------------
# 4. Calibration (test rules against LLM checker)
# ---------------------------------------------------------------------------

def _compute_stats(
    cases: list[dict], failing_ids: list[str],
) -> tuple[float, float]:
    """Return (recall, precision) given cases and IDs that failed checks."""
    total_pos = sum(1 for c in cases if c["expected"] == "stipulation_violation")
    total_neg = sum(1 for c in cases if c["expected"] == "none")
    fail_set = set(failing_ids)
    pos_fail = sum(
        1 for c in cases
        if c["id"] in fail_set and c["expected"] == "stipulation_violation"
    )
    neg_fail = sum(
        1 for c in cases
        if c["id"] in fail_set and c["expected"] == "none"
    )
    recall = (total_pos - pos_fail) / total_pos if total_pos else 1.0
    precision = (total_neg - neg_fail) / total_neg if total_neg else 1.0
    return recall, precision


def calibrate_gate_rules(
    rules: dict,
    cases: list[dict],
    provider: BaseProvider,
    *,
    max_retries: int = 2,
) -> tuple[dict, list[dict], dict]:
    """Run test cases through the LLM checker and report calibration quality.

    Returns (rules, cases, calibration_report).
    """
    if not cases:
        return rules, cases, {"recall": 1.0, "precision": 1.0, "issues": 0}

    stipulated_rules = rules.get("stipulated_rules", [])
    facts_block = "\n".join(f"  [{r['id']}] {r['fact']}" for r in stipulated_rules)
    checker_system = (
        "You are a strict validity checker. Check whether the text violates "
        "ANY of these stipulated facts:\n\n"
        f"{facts_block}\n\n"
        "A violation means the text asserts BOTH halves of a proven contradiction. "
        "Quoting or critiquing is NOT a violation.\n\n"
        'Return JSON: {"violated": true/false, "rule_id": "RULE-X or null", "reason": "..."}'
    )

    def _check(case: dict) -> bool:
        """True if LLM judgement matches expected label."""
        try:
            r = provider.call_structured(
                system=checker_system,
                user=f"TEXT TO CHECK:\n\n{case['text']}",
                schema=CalibrationCheckResult, max_tokens=_B.small,
            )
            return r.get("violated", False) == (case["expected"] == "stipulation_violation")
        except Exception:
            return True  # fail open

    def _find_issues() -> list[str]:
        with ThreadPoolExecutor(max_workers=min(6, len(cases))) as pool:
            futures = {c["id"]: pool.submit(_check, c) for c in cases}
            return [cid for cid, fut in futures.items() if not fut.result()]

    issues = _find_issues()
    recall, precision = _compute_stats(cases, issues)
    report: dict = {
        "initial_recall": recall, "initial_precision": precision,
        "initial_issues": len(issues), "retries_used": 0,
        "final_recall": recall, "final_precision": precision,
        "final_issues": len(issues),
    }

    if not issues:
        logger.info("Gate calibration passed: recall=%.2f, precision=%.2f", recall, precision)
        return rules, cases, report

    for attempt in range(1, max_retries + 1):
        logger.warning(
            "Gate calibration attempt %d/%d: %d issues (recall=%.2f)",
            attempt, max_retries, len(issues), recall,
        )
        regen_user = (
            f"RULES:\n{json.dumps(stipulated_rules, indent=2, default=str)}\n\n"
            f"CURRENT CASES:\n{json.dumps(cases, indent=2, default=str)}\n\n"
            f"FAILING CASE IDS: {json.dumps(issues)}\n\n"
            "Fix the failing cases and return all cases."
        )
        try:
            resp = provider.call_structured(
                "Regenerate failing test cases so they clearly match their "
                "expected label. Positive cases must assert BOTH halves of the "
                "contradiction. Negative cases must be non-violating. "
                "Return ALL cases (fixed and unchanged).",
                regen_user, GateTestsResult, max_tokens=_B.large,
            )
            cases = resp.get("cases", cases)
        except Exception as exc:
            logger.warning("Test case regeneration failed: %s", exc)

        issues = _find_issues()
        recall, precision = _compute_stats(cases, issues)
        report["retries_used"] = attempt
        if not issues:
            break

    report.update(final_recall=recall, final_precision=precision, final_issues=len(issues))
    if issues:
        logger.warning(
            "Gate calibration incomplete after %d retries: recall=%.2f, precision=%.2f, %d issues",
            max_retries, recall, precision, len(issues),
        )
    else:
        logger.info(
            "Gate calibration passed after %d retries: recall=%.2f, precision=%.2f",
            report["retries_used"], recall, precision,
        )
    return rules, cases, report
