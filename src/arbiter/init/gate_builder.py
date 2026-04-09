"""Generate validity gate rules and test cases from identified contradictions.

Part of Arbiter's agentic init pipeline. Produces:
- Stipulated rules with regex bad_patterns / denial_patterns
- Seed term definitions
- Entailment check facts (plain English for the LLM backstop)
- Gold-standard test cases for each rule
- Anticipated escape routes for each contradiction
"""

from __future__ import annotations

import json
import logging
import re
import textwrap

from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# JSON schemas for structured LLM responses
# ---------------------------------------------------------------------------
_RULES_SCHEMA = {
    "type": "object",
    "properties": {
        "stipulated_rules": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Short rule ID like RULE-1."},
                    "fact": {
                        "type": "string",
                        "description": "Plain-English statement of the stipulated fact.",
                    },
                    "bad_patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Regex patterns (Python re syntax, case-insensitive) that detect "
                            "a turn violating this rule. Use word boundaries (\\b) and alternation."
                        ),
                    },
                    "denial_patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Regex patterns that indicate the speaker is explicitly DENYING "
                            "the bad claim (i.e. adopting a repair). If a denial pattern matches, "
                            "the bad_pattern match is suppressed."
                        ),
                    },
                },
                "required": ["id", "fact", "bad_patterns", "denial_patterns"],
                "additionalProperties": False,
            },
        },
        "seed_terms": {
            "type": "object",
            "additionalProperties": {"type": "string"},
            "description": "Key terms with definitions, e.g. {'G': 'The universal DAG...'}.",
        },
        "entailment_facts": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "Plain-English facts for the LLM entailment backstop. "
                "Each should be a single sentence stating a stipulated truth."
            ),
        },
    },
    "required": ["stipulated_rules", "seed_terms", "entailment_facts"],
    "additionalProperties": False,
}

_TESTS_SCHEMA = {
    "type": "object",
    "properties": {
        "cases": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Test ID like RULE-1_direct, RULE-1_paraphrase, RULE-1_negative.",
                    },
                    "expected": {
                        "type": "string",
                        "enum": ["stipulation_violation", "none"],
                        "description": "Whether this test case should fire a violation.",
                    },
                    "text": {
                        "type": "string",
                        "description": (
                            "Realistic, natural-sounding debate turn text. "
                            "2-4 sentences. Not just keywords."
                        ),
                    },
                },
                "required": ["id", "expected", "text"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["cases"],
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# Escape route anticipation
# ---------------------------------------------------------------------------

_ESCAPE_ROUTES_SYSTEM = textwrap.dedent("""\
    You are an expert debate strategist predicting how a defender of a
    theory will try to work around identified contradictions.

    For each contradiction, predict 2-4 "escape routes" a defender might
    use to avoid conceding the point.  Common escape strategies include:
    - Redefining a key term to dissolve the contradiction
    - Claiming two separate "modes" or "levels" that don't actually conflict
    - Retreating to a weaker version of the claim without acknowledging the retreat
    - Asserting the contradiction is only "apparent" without explaining why
    - Shifting to meta-level claims (e.g., "in a deeper sense...")
    - Invoking special conditions or exceptions not in the original theory
    - Conflating formal and informal usage of the same term

    For each escape route, provide:
    1. The strategy name (short description)
    2. Language patterns: specific phrases or constructions the defender
       would likely use when employing this escape
    3. How to catch it: what makes this escape illegitimate and how a
       gate rule should detect it

    Use the theory's own terminology from the KEY TERMS provided.

    Return a JSON object with key "escape_routes" containing an array.
""")

_ESCAPE_ROUTES_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "escape_routes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "contradiction_id": {
                        "type": "string",
                        "description": "Reference to the contradiction (claim_a vs claim_b).",
                    },
                    "routes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "strategy": {
                                    "type": "string",
                                    "description": "Short description of the escape strategy.",
                                },
                                "language_patterns": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Phrases the defender would use.",
                                },
                                "how_to_catch": {
                                    "type": "string",
                                    "description": "Why this escape is illegitimate and how to detect it.",
                                },
                            },
                            "required": ["strategy", "language_patterns", "how_to_catch"],
                        },
                    },
                },
                "required": ["contradiction_id", "routes"],
            },
        }
    },
    "required": ["escape_routes"],
}


def anticipate_escape_routes(
    contradictions: list[dict],
    key_terms: dict[str, str],
    provider: BaseProvider,
) -> list[dict]:
    """For each contradiction, predict how a defender might try to work around it.

    Returns list of::

        {
            "contradiction_id": "C1 vs C3",
            "routes": [
                {
                    "strategy": "Redefine the key term to dissolve the contradiction",
                    "language_patterns": ["in a deeper sense", "properly understood"],
                    "how_to_catch": "Flag any redefinition without explicit notice"
                },
                ...
            ]
        }
    """
    if not contradictions:
        return []

    contra_text = json.dumps(contradictions, indent=2, default=str)
    terms_text = json.dumps(key_terms, indent=2, default=str)

    user_msg = textwrap.dedent(f"""\
        CONTRADICTIONS:
        {contra_text}

        KEY TERMS:
        {terms_text}

        For each contradiction, predict 2-4 escape routes a defender might use.
    """)

    try:
        result = provider.call_structured(
            system=_ESCAPE_ROUTES_SYSTEM,
            user=user_msg,
            schema=_ESCAPE_ROUTES_RESPONSE_SCHEMA,
            max_tokens=6000,
        )
        escape_routes = result.get("escape_routes", [])
        logger.info(
            "Anticipated %d escape route groups for %d contradictions",
            len(escape_routes),
            len(contradictions),
        )
        return escape_routes
    except Exception as exc:
        logger.warning("Escape route anticipation failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# Rule generation
# ---------------------------------------------------------------------------

def _build_rules_prompt(
    contradictions: list[dict],
    key_terms: dict[str, str],
    escape_routes: list[dict] | None = None,
) -> tuple[str, str]:
    """Build (system, user) prompts for gate rule generation."""
    escape_route_instruction = ""
    if escape_routes:
        escape_route_instruction = textwrap.dedent("""\

        ESCAPE ROUTE PATTERNS TO CATCH:
        In addition to direct reassertions of disproven claims, your
        bad_patterns MUST also catch predicted ESCAPE ROUTES -- ways a
        defender might try to work around the contradiction without
        explicitly conceding it.  The anticipated escape routes are
        provided below.  For each escape route, generate regex patterns
        that catch the specific language patterns listed.

        For example, if an escape route predicts a defender will say
        "in a deeper sense" or "properly understood" to redefine a term,
        generate a pattern like:
            \\b(in a deeper sense|properly understood|metatheoretic)\\b
        """)

    system = textwrap.dedent("""\
        You are an expert at building regex-based content moderation rules for
        academic debate. Your task: given contradictions identified in a source
        document, a glossary of key terms, and anticipated escape routes that
        defenders might use, produce stipulated rules that will catch debate
        turns that reassert a disproven claim OR attempt an illegitimate escape.

        REQUIREMENTS FOR EACH RULE:
        1. id: short identifier like RULE-1, RULE-2, etc.
        2. fact: plain-English statement of the stipulated truth (1-2 sentences).
        3. bad_patterns: 4-12 Python regex patterns (re.IGNORECASE) that detect
           a turn violating this rule. Use:
           - Word boundaries (\\b) to avoid false matches
           - Alternation for synonyms: (add|create|instantiate)
           - Co-occurrence patterns: claim_A.*claim_B and claim_B.*claim_A
           - Variants: direct assertion, dual-mode rescue, "no contradiction" rescue
           - Escape route language patterns from the anticipated routes
        4. denial_patterns: 2-4 regex patterns detecting explicit denial/repair
           (e.g. "I adopt repair path A", "drop X as Y"). When a denial matches,
           it suppresses the bad_pattern hit.
        {escape_route_instruction}
        REQUIREMENTS FOR SEED TERMS:
        - Include every formal term that appears in the contradictions.
        - Each definition should be 1-2 sentences.

        REQUIREMENTS FOR ENTAILMENT FACTS:
        - One plain-English fact per rule, suitable as a prompt for an LLM
          entailment checker.
        - Format: "[RULE-ID] statement of stipulated truth."

        Return valid JSON matching the schema. Regex patterns must be valid Python re syntax.
    """).format(escape_route_instruction=escape_route_instruction)

    # Build escape routes text if available
    escape_text = ""
    if escape_routes:
        escape_text = f"\nANTICIPATED ESCAPE ROUTES:\n{json.dumps(escape_routes, indent=2, default=str)}\n"

    user = textwrap.dedent(f"""\
        CONTRADICTIONS:
        {json.dumps(contradictions, indent=2, default=str)}

        KEY TERMS:
        {json.dumps(key_terms, indent=2, default=str)}
        {escape_text}
        Generate stipulated_rules, seed_terms, and entailment_facts.
    """)
    return system, user


def _validate_regex_patterns(rules: list[dict]) -> list[dict]:
    """Validate all regex patterns compile. Remove invalid ones and log warnings."""
    cleaned = []
    for rule in rules:
        valid_bad = []
        for pat in rule.get("bad_patterns", []):
            try:
                re.compile(pat, re.IGNORECASE)
                valid_bad.append(pat)
            except re.error as exc:
                logger.warning("Invalid bad_pattern in %s: %r -> %s", rule["id"], pat, exc)
        valid_denial = []
        for pat in rule.get("denial_patterns", []):
            try:
                re.compile(pat, re.IGNORECASE)
                valid_denial.append(pat)
            except re.error as exc:
                logger.warning("Invalid denial_pattern in %s: %r -> %s", rule["id"], pat, exc)
        cleaned.append({
            **rule,
            "bad_patterns": valid_bad,
            "denial_patterns": valid_denial,
        })
    return cleaned


def _extract_json_from_text(text: str) -> dict | None:
    """Extract a JSON object from LLM text output using regex + json.loads."""
    # Try to find JSON block in markdown code fence
    match = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find raw JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def generate_gate_rules(
    contradictions: list[dict],
    key_terms: dict[str, str],
    provider: BaseProvider,
    *,
    escape_routes: list[dict] | None = None,
) -> dict:
    """Generate validity gate configuration from identified contradictions.

    Uses the LLM to produce regex patterns tailored to the specific
    contradiction language and anticipated escape routes, then validates
    every pattern compiles.

    Parameters
    ----------
    contradictions:
        Output of ``claim_extractor.identify_contradictions``.
    key_terms:
        Glossary mapping term names to definitions.
    provider:
        An Arbiter ``BaseProvider`` instance for LLM calls.
    escape_routes:
        Output of ``anticipate_escape_routes()`` (optional).
        When provided, generated patterns will also catch predicted
        escape strategies.

    Returns
    -------
    dict with keys:
        - ``stipulated_rules``: list of rule dicts with id, fact, bad_patterns, denial_patterns
        - ``seed_terms``: dict mapping term -> definition
        - ``entailment_facts``: list of plain-English stipulated facts
    """
    system, user = _build_rules_prompt(contradictions, key_terms, escape_routes)
    logger.info("Generating gate rules via LLM...")

    # Use call_with_retry + JSON extraction for robustness with complex
    # nested schemas (avoids additionalProperties issues across providers)
    try:
        response = provider.call_structured(system, user, _RULES_SCHEMA, max_tokens=6000)
    except Exception as exc:
        logger.warning(
            "call_structured failed for gate rules (%s); "
            "falling back to call_with_retry + JSON extraction",
            exc,
        )
        try:
            raw_text = provider.call_with_retry(
                system=system + f"\n\nJSON Schema:\n{json.dumps(_RULES_SCHEMA, indent=2)}",
                user=user,
                max_tokens=6000,
            )
            response = _extract_json_from_text(raw_text)
            if response is None:
                logger.error("Could not extract JSON from gate rules response")
                return {
                    "stipulated_rules": [],
                    "seed_terms": dict(key_terms),
                    "entailment_facts": [],
                }
        except Exception as exc2:
            logger.error("Gate rule generation failed entirely: %s", exc2)
            return {
                "stipulated_rules": [],
                "seed_terms": dict(key_terms),
                "entailment_facts": [],
            }

    # Validate regex patterns
    response["stipulated_rules"] = _validate_regex_patterns(
        response.get("stipulated_rules", [])
    )

    n_rules = len(response["stipulated_rules"])
    n_patterns = sum(
        len(r["bad_patterns"]) for r in response["stipulated_rules"]
    )
    logger.info("Generated %d rules with %d total bad_patterns.", n_rules, n_patterns)

    return response


# ---------------------------------------------------------------------------
# Test case generation
# ---------------------------------------------------------------------------

def _build_tests_prompt(rules: dict, claims: list[dict]) -> tuple[str, str]:
    """Build (system, user) prompts for gate test case generation."""
    system = textwrap.dedent("""\
        You are generating gold-standard test cases for a validity gate in an
        academic debate system. The gate uses regex patterns to detect when a
        debater reasserts a disproven claim.

        For EACH rule, generate exactly 3 test cases:
        1. A DIRECT positive case (expected: stipulation_violation) that uses
           the exact terminology of the contradiction. 2-4 natural sentences.
        2. A PARAPHRASE positive case (expected: stipulation_violation) that
           restates the violation using synonyms and different phrasing, but
           should still be caught by the regex patterns. 2-4 natural sentences.
        3. A NEGATIVE case (expected: none) that discusses the same topic area
           but does NOT violate the rule. This might be a turn that explicitly
           adopts a repair or a skeptic's critique. 2-4 natural sentences.

        CRITICAL:
        - Positive cases MUST contain text that will match at least one of the
          rule's bad_patterns (given below).
        - Negative cases MUST NOT match any bad_pattern, OR must also match a
          denial_pattern.
        - Text should sound like a real debate turn, not a keyword list.
        - Use the rule's id as prefix: RULE-1_direct, RULE-1_paraphrase, RULE-1_negative.
    """)

    rules_json = json.dumps(rules.get("stipulated_rules", []), indent=2, default=str)
    claims_json = json.dumps(claims[:15], indent=2, default=str)

    user = textwrap.dedent(f"""\
        RULES (with their regex patterns):
        {rules_json}

        CLAIMS (for context on the source material):
        {claims_json}

        Generate test cases. Each positive case MUST contain text that matches
        at least one bad_pattern from its rule. Review the patterns carefully.
    """)
    return system, user


def _test_pattern_coverage(
    rules: list[dict], cases: list[dict]
) -> tuple[list[dict], list[str]]:
    """Test that positive cases match their rule's patterns and negatives don't.

    Returns (cases, issues) where issues lists any problems found.
    """
    issues: list[str] = []
    rules_by_id = {}
    for rule in rules:
        # Extract base rule id from test case ids like RULE-1_direct
        rules_by_id[rule["id"]] = rule

    for case in cases:
        # Derive rule id from case id (e.g. "RULE-1_direct" -> "RULE-1")
        parts = case["id"].rsplit("_", 1)
        rule_id = parts[0] if len(parts) == 2 else case["id"]
        rule = rules_by_id.get(rule_id)
        if not rule:
            # Try without last component
            issues.append(f"Case {case['id']}: no matching rule found for id {rule_id}")
            continue

        text = case["text"]
        is_positive = case["expected"] == "stipulation_violation"

        if is_positive:
            # Check that at least one bad_pattern matches
            matched = False
            for pat in rule["bad_patterns"]:
                try:
                    if re.search(pat, text, re.IGNORECASE):
                        matched = True
                        break
                except re.error:
                    pass
            if not matched:
                issues.append(
                    f"Case {case['id']}: POSITIVE case does not match any "
                    f"bad_pattern for rule {rule['id']}"
                )
        else:
            # Check that either no bad_pattern matches, or a denial also matches
            bad_match = False
            for pat in rule["bad_patterns"]:
                try:
                    if re.search(pat, text, re.IGNORECASE):
                        bad_match = True
                        break
                except re.error:
                    pass
            if bad_match:
                denial_match = False
                for pat in rule.get("denial_patterns", []):
                    try:
                        if re.search(pat, text, re.IGNORECASE):
                            denial_match = True
                            break
                    except re.error:
                        pass
                if not denial_match:
                    issues.append(
                        f"Case {case['id']}: NEGATIVE case matches a bad_pattern "
                        f"but no denial_pattern for rule {rule['id']}"
                    )

    return cases, issues


def _build_fix_prompt(
    rules: list[dict], cases: list[dict], issues: list[str]
) -> tuple[str, str]:
    """Build a repair prompt for test cases that fail pattern coverage."""
    system = textwrap.dedent("""\
        You are fixing test cases for a regex-based validity gate. Some test cases
        failed coverage checks. Fix them so:
        - Positive cases (expected: stipulation_violation) match at least one bad_pattern
        - Negative cases (expected: none) either match no bad_pattern, or also match a denial_pattern

        Return ALL cases (fixed and unchanged) in the same format.
        Adjust the TEXT of failing cases to include phrases that match the patterns.
        Do NOT change the id or expected fields.
    """)

    user = textwrap.dedent(f"""\
        RULES:
        {json.dumps(rules, indent=2, default=str)}

        CURRENT CASES:
        {json.dumps(cases, indent=2, default=str)}

        ISSUES:
        {json.dumps(issues, indent=2)}

        Fix the cases and return all of them.
    """)
    return system, user


def calibrate_gate_rules(
    rules: dict,
    cases: list[dict],
    provider: BaseProvider,
    *,
    max_retries: int = 2,
) -> tuple[dict, list[dict], dict]:
    """Self-calibration loop: test patterns against cases, regenerate if needed.

    Parameters
    ----------
    rules:
        Output of ``generate_gate_rules()``.
    cases:
        Output of ``generate_gate_tests()``.
    provider:
        LLM provider for regeneration.
    max_retries:
        Maximum number of pattern regeneration attempts.

    Returns
    -------
    tuple of (rules, cases, calibration_report)
        - rules: possibly updated rules with improved patterns
        - cases: possibly updated test cases
        - calibration_report: dict with recall/precision stats
    """
    stipulated_rules = rules.get("stipulated_rules", [])
    _, issues = _test_pattern_coverage(stipulated_rules, cases)

    total_positive = sum(1 for c in cases if c["expected"] == "stipulation_violation")
    total_negative = sum(1 for c in cases if c["expected"] == "none")

    # Count how many positive cases matched
    positive_matched = total_positive - sum(
        1 for iss in issues if "POSITIVE case does not match" in iss
    )
    negative_clean = total_negative - sum(
        1 for iss in issues if "NEGATIVE case matches" in iss
    )

    recall = positive_matched / total_positive if total_positive > 0 else 1.0
    precision = negative_clean / total_negative if total_negative > 0 else 1.0

    report: dict = {
        "initial_recall": recall,
        "initial_precision": precision,
        "initial_issues": len(issues),
        "retries_used": 0,
        "final_recall": recall,
        "final_precision": precision,
        "final_issues": len(issues),
    }

    if not issues:
        logger.info(
            "Gate calibration passed: recall=%.2f, precision=%.2f",
            recall, precision,
        )
        return rules, cases, report

    # Retry loop: regenerate patterns for rules with failing positive cases
    for attempt in range(1, max_retries + 1):
        logger.warning(
            "Gate calibration attempt %d/%d: %d issues (recall=%.2f)",
            attempt, max_retries, len(issues), recall,
        )

        # Identify which rules have failing positive cases
        failing_rule_ids = set()
        for iss in issues:
            if "POSITIVE case does not match" in iss:
                # Extract rule ID from issue text
                for rule in stipulated_rules:
                    if rule["id"] in iss:
                        failing_rule_ids.add(rule["id"])
                        break

        if failing_rule_ids:
            # Regenerate patterns for failing rules
            _regenerate_patterns(
                rules, cases, failing_rule_ids, provider,
            )
            stipulated_rules = rules.get("stipulated_rules", [])

        # Also fix test cases
        fix_system, fix_user = _build_fix_prompt(stipulated_rules, cases, issues)
        try:
            fix_response = provider.call_structured(
                fix_system, fix_user, _TESTS_SCHEMA, max_tokens=6000
            )
            cases = fix_response.get("cases", cases)
        except Exception as exc:
            logger.warning("Test case fix failed: %s", exc)

        _, issues = _test_pattern_coverage(stipulated_rules, cases)

        positive_matched = total_positive - sum(
            1 for iss in issues if "POSITIVE case does not match" in iss
        )
        negative_clean = total_negative - sum(
            1 for iss in issues if "NEGATIVE case matches" in iss
        )
        recall = positive_matched / total_positive if total_positive > 0 else 1.0
        precision = negative_clean / total_negative if total_negative > 0 else 1.0
        report["retries_used"] = attempt

        if not issues:
            break

    report["final_recall"] = recall
    report["final_precision"] = precision
    report["final_issues"] = len(issues)

    if issues:
        logger.warning(
            "Gate calibration incomplete after %d retries: "
            "recall=%.2f, precision=%.2f, %d issues remaining",
            max_retries, recall, precision, len(issues),
        )
    else:
        logger.info(
            "Gate calibration passed after %d retries: recall=%.2f, precision=%.2f",
            report["retries_used"], recall, precision,
        )

    return rules, cases, report


def _regenerate_patterns(
    rules: dict,
    cases: list[dict],
    failing_rule_ids: set[str],
    provider: BaseProvider,
) -> None:
    """Regenerate bad_patterns for specific rules that have failing test cases."""
    stipulated_rules = rules.get("stipulated_rules", [])

    for rule in stipulated_rules:
        if rule["id"] not in failing_rule_ids:
            continue

        # Find positive test cases for this rule
        positive_texts = []
        for case in cases:
            parts = case["id"].rsplit("_", 1)
            case_rule_id = parts[0] if len(parts) == 2 else case["id"]
            if case_rule_id == rule["id"] and case["expected"] == "stipulation_violation":
                positive_texts.append(case["text"])

        if not positive_texts:
            continue

        system = textwrap.dedent("""\
            You are fixing regex patterns for a validity gate rule.
            The current patterns FAIL to match the positive test cases below.

            Generate 4-8 NEW regex patterns (Python re syntax, case-insensitive)
            that WILL match the positive test case texts.  Use:
            - Word boundaries (\\b)
            - Alternation for key phrases
            - Broader patterns that catch the semantic content

            Return a JSON object with a single key "bad_patterns" containing
            an array of regex pattern strings.
        """)

        user = (
            f"RULE: {rule['id']}\n"
            f"FACT: {rule['fact']}\n\n"
            f"CURRENT PATTERNS (failing):\n{json.dumps(rule['bad_patterns'], indent=2)}\n\n"
            f"POSITIVE TEST CASES THAT MUST MATCH:\n"
            + "\n---\n".join(positive_texts)
        )

        try:
            result = provider.call_structured(
                system=system,
                user=user,
                schema={
                    "type": "object",
                    "properties": {
                        "bad_patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["bad_patterns"],
                    "additionalProperties": False,
                },
                max_tokens=2000,
            )
            new_patterns = result.get("bad_patterns", [])
            # Validate and merge
            valid_new = []
            for pat in new_patterns:
                try:
                    re.compile(pat, re.IGNORECASE)
                    valid_new.append(pat)
                except re.error:
                    pass
            if valid_new:
                # Keep old patterns and add new ones (deduplicated)
                existing = set(rule["bad_patterns"])
                for pat in valid_new:
                    if pat not in existing:
                        rule["bad_patterns"].append(pat)
                logger.info(
                    "Regenerated patterns for %s: %d new patterns added",
                    rule["id"], len(valid_new),
                )
        except Exception as exc:
            logger.warning("Pattern regeneration failed for %s: %s", rule["id"], exc)


def generate_gate_tests(
    rules: dict,
    claims: list[dict],
    provider: BaseProvider,
) -> list[dict]:
    """Generate gold-standard test cases for the validity gate.

    For each rule, generates:
    - 2 positive cases (should fire): 1 direct, 1 paraphrase
    - 1 negative case (should NOT fire): a clean turn mentioning the topic

    Generated test cases are validated against the rule's regex patterns.
    If a positive case does not match any bad_pattern, the LLM is asked to
    regenerate with the error feedback (up to 2 attempts).

    Parameters
    ----------
    rules:
        Output of :func:`generate_gate_rules`.
    claims:
        Output of ``pdf_reader.extract_claims`` (for context).
    provider:
        An Arbiter ``BaseProvider`` instance for LLM calls.

    Returns
    -------
    list of dicts, each with keys: id, expected, text.
    """
    system, user = _build_tests_prompt(rules, claims)
    logger.info("Generating gate test cases via LLM...")

    response = provider.call_structured(system, user, _TESTS_SCHEMA, max_tokens=6000)
    cases = response.get("cases", [])

    stipulated_rules = rules.get("stipulated_rules", [])

    # Validate pattern coverage
    cases, issues = _test_pattern_coverage(stipulated_rules, cases)

    # Retry loop: fix cases that fail coverage
    max_retries = 2
    for attempt in range(1, max_retries + 1):
        if not issues:
            break
        logger.warning(
            "Test coverage issues (attempt %d/%d): %s",
            attempt, max_retries, "; ".join(issues[:5]),
        )
        fix_system, fix_user = _build_fix_prompt(stipulated_rules, cases, issues)
        fix_response = provider.call_structured(
            fix_system, fix_user, _TESTS_SCHEMA, max_tokens=6000
        )
        cases = fix_response.get("cases", cases)
        cases, issues = _test_pattern_coverage(stipulated_rules, cases)

    if issues:
        logger.warning(
            "Unresolved test coverage issues after %d retries: %s",
            max_retries, "; ".join(issues),
        )
    else:
        logger.info("All %d test cases pass pattern coverage checks.", len(cases))

    return cases
