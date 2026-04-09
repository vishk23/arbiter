"""Web search via Tavily (optional dependency)."""

from __future__ import annotations

import os
import sys
from typing import Dict, List


class WebSearcher:
    """Thin wrapper around the Tavily search API with graceful degradation."""

    def __init__(self, provider: str = "tavily") -> None:
        self._provider = provider
        self._warned = False

    # ------------------------------------------------------------------
    def search(self, query: str, k: int = 2) -> List[Dict]:
        """Return top-*k* web hits as ``[{source, score, excerpt}]``.

        Returns an empty list when Tavily is not installed or the
        ``TAVILY_API_KEY`` environment variable is missing.
        """
        if self._provider != "tavily":
            return []

        api_key = os.getenv("TAVILY_API_KEY", "")
        if not api_key:
            if not self._warned:
                print(
                    "[retrieval] TAVILY_API_KEY not set; web search disabled.",
                    file=sys.stderr,
                )
                self._warned = True
            return []

        try:
            from tavily import TavilyClient  # type: ignore[import-untyped]
        except ImportError:
            if not self._warned:
                print(
                    "[retrieval] tavily package not installed; web search disabled.",
                    file=sys.stderr,
                )
                self._warned = True
            return []

        try:
            client = TavilyClient(api_key=api_key)
            # Tavily enforces a 400-char query limit; truncate to 380 for safety.
            resp = client.search(
                query=query[:380], max_results=k, search_depth="advanced"
            )
            raw_results = resp.get("results", []) if isinstance(resp, dict) else []
            results: List[Dict] = []
            for r in raw_results:
                results.append(
                    {
                        "source": r.get("url", ""),
                        "score": round(float(r.get("score", 0.0) or 0.0), 4),
                        "excerpt": (r.get("content") or "").strip(),
                    }
                )
            return results
        except Exception as exc:
            print(f"[retrieval] tavily error: {exc}", file=sys.stderr)
            return []
