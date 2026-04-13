"""Find and download primary sources for debate preparation."""

from __future__ import annotations

import logging
import re
import textwrap
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING

from arbiter.config import TokenBudgets
from arbiter.schemas import ClassifyResult, QueryResult, SynthResult

if TYPE_CHECKING:
    from arbiter.providers.base import BaseProvider
    from arbiter.retrieval.web_search import WebSearcher

logger = logging.getLogger(__name__)
_B = TokenBudgets()

# ---------------------------------------------------------------------------
# JSON schema for the query-generation step
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def find_sources(
    claims: list[dict],
    key_terms: dict[str, str],
    output_dir: str,
    provider: "BaseProvider",
    web_searcher: "WebSearcher | None" = None,
) -> list[str]:
    """Search the web for relevant primary sources and save as text files.

    Strategy:

    1. LLM identifies the key references/authorities cited or implied by
       the claims.
    2. For each, search via Tavily for summary content.
    3. Save as ``.txt`` files in *output_dir*.
    4. Return list of file paths created.

    If Tavily is unavailable, falls back to LLM-generated paraphrase
    summaries (clearly marked as ``[LLM-GENERATED]``).

    Parameters
    ----------
    claims:
        Extracted claims (each has ``id``, ``claim``, ``category``, etc.).
    key_terms:
        Seed terms dict, e.g. ``{"G": "The universal BIT DAG..."}``.
    output_dir:
        Directory to write source files into (created if missing).
    provider:
        The LLM used for query generation and fallback synthesis.
    web_searcher:
        Optional :class:`~arbiter.retrieval.web_search.WebSearcher`.
        When ``None`` or when searches return empty, the LLM fallback
        is used.

    Returns
    -------
    list[str]
        Absolute paths to the created source files.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Step 1: ask the LLM what to search for
    queries = _generate_queries(claims, key_terms, provider)
    logger.info("Generated %d search queries", len(queries))

    # Process queries in parallel (web search + LLM fallback are independent)
    def _process_query(q: dict) -> str:
        query_text = q["query"]
        filename = _sanitize_filename(q.get("filename", "source"))
        rationale = q.get("rationale", "")
        filepath = out / f"{filename}.txt"

        web_results = _try_web_search(query_text, web_searcher)
        if web_results:
            content = _format_web_results(query_text, rationale, web_results)
            filepath.write_text(content, encoding="utf-8")
            logger.info("Saved web source: %s (%d results)", filepath, len(web_results))
        else:
            content = _synthesize_from_llm(query_text, rationale, provider)
            filepath.write_text(content, encoding="utf-8")
            logger.info("Saved LLM-generated source: %s", filepath)

        return str(filepath.resolve())

    with ThreadPoolExecutor(max_workers=min(4, len(queries))) as pool:
        created = list(pool.map(_process_query, queries))

    logger.info("Source finder created %d files in %s", len(created), output_dir)
    return created


def classify_sources(
    source_paths: list[str],
    claims: list[dict],
    provider: "BaseProvider",
) -> dict[str, list[str]]:
    """Classify downloaded sources by relevance to each side.

    Reads the first 1000 characters of each source file and asks the
    LLM to classify it as counter-evidence, supports-theory, or
    neutral-reference.

    Parameters
    ----------
    source_paths:
        Absolute paths to source text files.
    claims:
        Extracted claims for context.
    provider:
        LLM provider for classification.

    Returns
    -------
    dict with keys:
        - ``"counter_evidence"``: list of paths
        - ``"supports_theory"``: list of paths
        - ``"neutral_reference"``: list of paths
    """
    result: dict[str, list[str]] = {
        "counter_evidence": [],
        "supports_theory": [],
        "neutral_reference": [],
    }

    if not source_paths:
        return result

    # Read first 1000 chars of each file
    source_snippets: list[dict[str, str]] = []
    for path in source_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                snippet = f.read(1000)
            source_snippets.append({"path": path, "snippet": snippet})
        except Exception as exc:
            logger.warning("Could not read source %s: %s", path, exc)
            result["neutral_reference"].append(path)

    if not source_snippets:
        return result

    # Build a compact claims summary
    claim_lines = "\n".join(
        f"  {c['id']}: {c['claim'][:100]}"
        for c in claims[:15]
    )

    snippets_text = "\n\n".join(
        f"FILE: {s['path']}\n{s['snippet']}"
        for s in source_snippets
    )

    system = textwrap.dedent("""\
        You are classifying reference sources for an adversarial debate.
        Given excerpts from downloaded source files and the claims of the
        theory being debated, classify each source as:

        - "counter_evidence": The source provides arguments, data, or
          frameworks that CHALLENGE or CONTRADICT the theory's claims.
        - "supports_theory": The source provides arguments, data, or
          frameworks that SUPPORT the theory's claims.
        - "neutral_reference": The source provides relevant background
          information but does not clearly favor either side.

        Return JSON matching the provided schema.
    """)

    user = textwrap.dedent(f"""\
        THEORY CLAIMS:
        {claim_lines}

        SOURCE EXCERPTS:
        {snippets_text}

        Classify each source file.
    """)

    try:
        response = provider.call_structured(
            system=system,
            user=user,
            schema=ClassifyResult,
            max_tokens=_B.small,
        )
        for entry in response.get("classifications", []):
            category = entry.get("category", "neutral_reference")
            path = entry.get("path", "")
            if category in result and path in source_paths:
                result[category].append(path)

        # Catch any unclassified sources
        classified = set()
        for paths_list in result.values():
            classified.update(paths_list)
        for path in source_paths:
            if path not in classified:
                result["neutral_reference"].append(path)

        logger.info(
            "Classified sources: %d counter, %d supporting, %d neutral",
            len(result["counter_evidence"]),
            len(result["supports_theory"]),
            len(result["neutral_reference"]),
        )
    except Exception as exc:
        logger.warning("Source classification failed: %s", exc)
        # Fall back: all neutral
        for path in source_paths:
            if path not in result["neutral_reference"]:
                result["neutral_reference"].append(path)

    return result


# ---------------------------------------------------------------------------
# Query generation
# ---------------------------------------------------------------------------

def _generate_queries(
    claims: list[dict],
    key_terms: dict[str, str],
    provider: "BaseProvider",
) -> list[dict]:
    """Ask the LLM to produce 2-4 targeted search queries."""
    claim_lines = "\n".join(
        f"  {c['id']}: [{c.get('category', '?')}] {c['claim']}"
        for c in claims
    )
    term_lines = "\n".join(
        f"  {k}: {v}" for k, v in key_terms.items()
    )

    system = textwrap.dedent("""\
        You are a research librarian preparing primary sources for an
        adversarial academic debate.  Given the claims and key terms of
        a theory, identify 2-4 web search queries that would surface the
        most important PRIMARY SOURCES (peer-reviewed papers, canonical
        textbooks, authoritative definitions) relevant to evaluating the
        theory.

        Rules:
        1. Target real, well-known sources -- e.g. "Pearl Causality 2009
           DAG axioms", "Jung Synchronicity 1952 definition".
        2. Do NOT generate queries for the theory itself (it is the
           subject of debate, not a source).
        3. Each query should target a DIFFERENT source or authority.
        4. Suggest a clean snake_case filename for each.
        5. Return 2-4 queries, no more.
    """)

    user = textwrap.dedent("""\
        CLAIMS from the theory under debate:
        {claims}

        KEY TERMS:
        {terms}

        Generate 2-4 search queries for the most important primary
        sources to inform this debate.
    """).format(claims=claim_lines, terms=term_lines)

    result = provider.call_structured(
        system=system,
        user=user,
        schema=QueryResult,
        max_tokens=_B.small,
    )

    queries = result.get("queries", [])

    # Enforce the 2-4 limit
    if len(queries) > 4:
        queries = queries[:4]
    if not queries:
        # Bare minimum fallback from key terms
        queries = [
            {
                "query": f"{term} definition academic",
                "rationale": f"Core term: {desc[:80]}",
                "filename": _sanitize_filename(term),
            }
            for term, desc in list(key_terms.items())[:3]
        ]

    return queries


# ---------------------------------------------------------------------------
# Web search
# ---------------------------------------------------------------------------

def _try_web_search(
    query: str,
    web_searcher: "WebSearcher | None",
) -> list[dict]:
    """Attempt a Tavily search; return empty list on any failure."""
    if web_searcher is None:
        return []
    try:
        return web_searcher.search(query, k=3)
    except Exception as exc:
        logger.warning("Web search failed for %r: %s", query, exc)
        return []


def _format_web_results(
    query: str,
    rationale: str,
    results: list[dict],
) -> str:
    """Format web search results into a clean source document."""
    lines = [
        f"SOURCE: Web search results for: {query}",
        f"RATIONALE: {rationale}",
        f"RETRIEVED: {len(results)} result(s)",
        "",
        "=" * 72,
    ]

    for i, r in enumerate(results, start=1):
        source_url = r.get("source", "unknown")
        score = r.get("score", 0.0)
        excerpt = r.get("excerpt", "").strip()
        lines.extend([
            "",
            f"--- Result {i} (relevance: {score:.2f}) ---",
            f"URL: {source_url}",
            "",
            excerpt,
            "",
        ])

    lines.extend([
        "=" * 72,
        "",
        "NOTE: These excerpts are retrieved from the web via Tavily search.",
        "They are summaries, not full texts.  Verify against the original",
        "sources before citing.",
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# LLM fallback synthesis
# ---------------------------------------------------------------------------

def _synthesize_from_llm(
    query: str,
    rationale: str,
    provider: "BaseProvider",
) -> str:
    """Generate a paraphrase-based source summary from LLM knowledge.

    Clearly marked as LLM-generated -- never fabricates citations.
    """
    system = textwrap.dedent("""\
        You are an academic research assistant.  The user needs a summary
        of a primary source or topic for debate preparation.  Provide a
        faithful paraphrase of the key ideas, definitions, axioms, and
        arguments from the well-known source implied by the query.

        CRITICAL RULES:
        1. Do NOT fabricate specific page numbers, edition details, or
           direct quotes unless you are CERTAIN they are correct.
        2. Mark anything you are uncertain about with [UNCERTAIN].
        3. Focus on the ideas, definitions, and logical structure that
           are widely accepted as part of this source.
        4. If you cannot provide useful information, say so honestly.
    """)

    user = (
        f"Provide a summary of the key ideas from: {query}\n\n"
        f"Context for why this matters: {rationale}"
    )

    result = provider.call_structured(
        system=system,
        user=user,
        schema=SynthResult,
        max_tokens=_B.medium,
    )

    title = result.get("title", query)
    content = result.get("content", "No content generated.")
    concepts = result.get("key_concepts", [])

    lines = [
        "[LLM-GENERATED SOURCE -- NOT from a live web search]",
        "",
        f"TOPIC: {title}",
        f"SEARCH QUERY: {query}",
        f"RATIONALE: {rationale}",
        "",
        "=" * 72,
        "",
        content,
        "",
        "=" * 72,
    ]

    if concepts:
        lines.extend([
            "",
            "KEY CONCEPTS:",
            *[f"  - {c}" for c in concepts],
        ])

    lines.extend([
        "",
        "WARNING: This summary was generated by an LLM from its training",
        "data, NOT retrieved from a live source.  It may contain errors.",
        "Do NOT treat this as a primary citation.  Verify all claims",
        "against the actual source before use in formal argumentation.",
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sanitize_filename(name: str) -> str:
    """Convert a string to a safe snake_case filename (no extension)."""
    # Lowercase, replace non-alnum with underscore, collapse runs
    s = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    # Truncate to reasonable length
    return s[:60] if s else "source"
