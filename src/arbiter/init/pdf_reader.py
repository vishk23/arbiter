"""PDF ingestion and LLM-driven claim extraction."""

from __future__ import annotations

import logging
import textwrap
from typing import TYPE_CHECKING

from arbiter.schemas import ClaimListResult

if TYPE_CHECKING:
    from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)

# Rough chars-per-token estimate (conservative for English prose).
_CHARS_PER_TOKEN = 4
_MAX_CHUNK_CHARS = 80_000 * _CHARS_PER_TOKEN  # ~80K tokens per chunk


# ---------------------------------------------------------------------------
# PDF -> Markdown
# ---------------------------------------------------------------------------

def read_pdf(path: str) -> str:
    """Convert a PDF file to LLM-ready markdown using *pymupdf4llm*.

    Raises ``ImportError`` with install instructions when the optional
    dependency is missing.
    """
    try:
        import pymupdf4llm  # noqa: F811
    except ImportError:
        raise ImportError(
            "pymupdf4llm is required for PDF ingestion. "
            "Install it with:  pip install arbiter-debate[pdf]"
        )
    try:
        return pymupdf4llm.to_markdown(path)
    except (TypeError, Exception):
        # Fallback: use the non-layout RAG helper which skips OCR
        import pymupdf4llm.helpers.pymupdf_rag as rag
        return rag.to_markdown(path)


# ---------------------------------------------------------------------------
# Chunking helpers
# ---------------------------------------------------------------------------

def _chunk_text(text: str, max_chars: int = _MAX_CHUNK_CHARS) -> list[str]:
    """Split *text* into chunks that each fit under the token budget.

    Tries to split on section headings (lines starting with ``#``).
    Falls back to splitting on double-newlines, then on hard character
    boundaries if necessary.
    """
    if len(text) <= max_chars:
        return [text]

    # Try splitting on markdown headings first.
    import re
    sections: list[str] = re.split(r"(?=\n#{1,3} )", text)

    chunks: list[str] = []
    current = ""
    for section in sections:
        if len(current) + len(section) > max_chars and current:
            chunks.append(current)
            current = ""
        # If a single section exceeds the limit, split it further.
        if len(section) > max_chars:
            for para in section.split("\n\n"):
                if len(current) + len(para) + 2 > max_chars and current:
                    chunks.append(current)
                    current = ""
                if len(para) > max_chars:
                    # Hard split as last resort.
                    while para:
                        space = max_chars - len(current)
                        current += para[:space]
                        para = para[space:]
                        if len(current) >= max_chars:
                            chunks.append(current)
                            current = ""
                else:
                    current = current + "\n\n" + para if current else para
        else:
            current = current + section if current else section
    if current.strip():
        chunks.append(current)
    return chunks


# ---------------------------------------------------------------------------
# Claim extraction
# ---------------------------------------------------------------------------

_EXTRACTION_SYSTEM = textwrap.dedent("""\
    You are an expert philosophical and scientific analyst.  Your job is to
    extract EVERY distinct claim from the provided document text.

    Rules:
    1. Be EXHAUSTIVE.  Extract all claims — obvious ones, subtle ones,
       implicit assumptions, and premises that the author takes for granted.
    2. Each claim must be a single, self-contained assertion.
    3. Categorise each claim:
       - "structural"      — about the structure or topology of a model/system
       - "logical"         — a logical inference or deduction
       - "empirical"       — about observable/measurable facts
       - "definitional"    — defining a term or concept
       - "autobiographical"— about the author's personal experience
    4. Flag ``is_formal`` = true when the claim could be encoded in formal
       logic, mathematics, or checked with an SMT solver like Z3.
    5. Note dependencies: if claim C3 relies on C1, put "C1" in
       ``depends_on`` for C3.
    6. Extract the nearest supporting quote from the text.  If there is no
       direct quote, use an empty string.
    7. Note the section heading or page where the claim appears.

    Return a JSON object matching the provided schema.  Do NOT wrap the
    output in markdown fences.
""")


def extract_claims(
    text: str,
    provider: "BaseProvider",
    *,
    max_tokens: int = 16000,
) -> list[dict]:
    """Use the LLM to extract structured claims from *text*.

    If the text exceeds the token budget it is chunked by section and
    each chunk is processed independently.  Claim IDs are re-numbered
    to stay globally unique across chunks, and cross-chunk ``depends_on``
    references are updated accordingly.

    Returns a list of claim dicts (see module docstring for shape).
    """
    chunks = _chunk_text(text)
    all_claims: list[dict] = []
    id_offset = 0

    for idx, chunk in enumerate(chunks):
        logger.info(
            "Extracting claims from chunk %d/%d (%d chars)",
            idx + 1,
            len(chunks),
            len(chunk),
        )
        user_msg = (
            f"Extract all claims from the following document text "
            f"(chunk {idx + 1}/{len(chunks)}):\n\n{chunk}"
        )
        result = provider.call_structured(
            system=_EXTRACTION_SYSTEM,
            user=user_msg,
            schema=ClaimListResult,
            max_tokens=max_tokens,
        )
        chunk_claims: list[dict] = result.get("claims", [])

        # Re-number IDs so they don't collide across chunks.
        if id_offset > 0:
            _renumber_claims(chunk_claims, id_offset)

        all_claims.extend(chunk_claims)
        id_offset = len(all_claims)

    return all_claims


def _renumber_claims(claims: list[dict], offset: int) -> None:
    """Shift all claim IDs and ``depends_on`` refs by *offset* in-place."""
    import re

    def _shift(cid: str) -> str:
        m = re.match(r"C(\d+)", cid)
        if m:
            return f"C{int(m.group(1)) + offset}"
        return cid

    old_to_new: dict[str, str] = {}
    for claim in claims:
        old_id = claim["id"]
        new_id = _shift(old_id)
        old_to_new[old_id] = new_id
        claim["id"] = new_id

    for claim in claims:
        claim["depends_on"] = [
            old_to_new.get(dep, _shift(dep)) for dep in claim.get("depends_on", [])
        ]
