"""Combined retrieval interface — local corpus + web search."""

from __future__ import annotations

from typing import TYPE_CHECKING

from arbiter.retrieval.local_index import LocalIndex
from arbiter.retrieval.web_search import WebSearcher

if TYPE_CHECKING:
    from arbiter.config import RetrievalConfig


class Retriever:
    """Unified retriever that merges local and web results.

    Accepts an optional :class:`RetrievalConfig`; when ``None``, all
    search calls return the no-sources sentinel.
    """

    def __init__(self, config: RetrievalConfig | None) -> None:
        self._local: LocalIndex | None = None
        self._web: WebSearcher | None = None

        if config is not None:
            if config.local is not None:
                self._local = LocalIndex(config.local.sources_dir)
            if config.web is not None:
                self._web = WebSearcher(provider=config.web.provider)

    # ------------------------------------------------------------------
    def retrieve(self, query: str, k_local: int = 2, k_web: int = 2) -> str:
        """Return a formatted string of primary-source excerpts.

        Falls back to ``"[no sources available]"`` when both backends
        return nothing.
        """
        local_hits = self._local.search(query, k_local) if self._local else []
        web_hits = self._web.search(query, k_web) if self._web else []

        if not local_hits and not web_hits:
            return "[no sources available]"

        lines: list[str] = ["PRIMARY SOURCES:"]
        for h in local_hits:
            lines.append(f"\n[local: {h['source']}, score={h['score']}]")
            lines.append(h["excerpt"])
        for h in web_hits:
            lines.append(f"\n[web: {h['source']}, score={h['score']}]")
            lines.append(h["excerpt"])
        return "\n".join(lines) + "\n"
