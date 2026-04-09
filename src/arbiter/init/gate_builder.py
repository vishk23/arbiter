"""Generate validity gate rules and test cases from identified contradictions.

Part of Arbiter's agentic init pipeline. Produces:
- Stipulated rules with regex bad_patterns / denial_patterns
- Seed term definitions
- Entailment check facts (plain English for the LLM backstop)
- Gold-standard test cases for each rule
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
# Rule generation
# ---------------------------------------------------------------------------

def _build_rules_prompt(
    contradictions: list[dict], key_terms: dict[str, str]
) -> tuple[str, str]:
    """Build (system, user) prompts for gate rule generation."""
    system = textwrap.dedent("""\
        You are an expert at building regex-based content moderation rules for
        academic debate. Your task: given contradictions identified in a source
        document and a glossary of key terms, produce stipulated rules that will
        catch debate turns that reassert a disproven claim.

        REQUIREMENTS FOR EACH RULE:
        1. id: short identifier like RULE-1, RULE-2, etc.
        2. fact: plain-English statement of the stipulated truth (1-2 sentences).
        3. bad_patterns: 4-12 Python regex patterns (re.IGNORECASE) that detect
           a turn violating this rule. Use:
           - Word boundaries (\\b) to avoid false matches
           - Alternation for synonyms: (add|create|instantiate)
           - Co-occurrence patterns: claim_A.*claim_B and claim_B.*claim_A
           - Variants: direct assertion, dual-mode rescue, "no contradiction" rescue
        4. denial_patterns: 2-4 regex patterns detecting explicit denial/repair
           (e.g. "I adopt repair path A", "drop X as Y"). When a denial matches,
           it suppresses the bad_pattern hit.

        REQUIREMENTS FOR SEED TERMS:
        - Include every formal term that appears in the contradictions.
        - Each definition should be 1-2 sentences.

        REQUIREMENTS FOR ENTAILMENT FACTS:
        - One plain-English fact per rule, suitable as a prompt for an LLM
          entailment checker.
        - Format: "[RULE-ID] statement of stipulated truth."

        Return valid JSON matching the schema. Regex patterns must be valid Python re syntax.
    """)

    user = textwrap.dedent(f"""\
        CONTRADICTIONS:
        {json.dumps(contradictions, indent=2, default=str)}

        KEY TERMS:
        {json.dumps(key_terms, indent=2, default=str)}

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


def generate_gate_rules(
    contradictions: list[dict],
    key_terms: dict[str, str],
    provider: BaseProvider,
) -> dict:
    """Generate validity gate configuration from identified contradictions.

    Uses the LLM to produce regex patterns tailored to the specific
    contradiction language, then validates every pattern compiles.

    Parameters
    ----------
    contradictions:
        Output of ``claim_extractor.identify_contradictions``.
    key_terms:
        Glossary mapping term names to definitions.
    provider:
        An Arbiter ``BaseProvider`` instance for LLM calls.

    Returns
    -------
    dict with keys:
        - ``stipulated_rules``: list of rule dicts with id, fact, bad_patterns, denial_patterns
        - ``seed_terms``: dict mapping term -> definition
        - ``entailment_facts``: list of plain-English stipulated facts
    """
    system, user = _build_rules_prompt(contradictions, key_terms)
    logger.info("Generating gate rules via LLM...")

    response = provider.call_structured(system, user, _RULES_SCHEMA, max_tokens=6000)

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
