"""TF-IDF local corpus search over .txt files."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

# sklearn is optional — fall back to keyword overlap
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    _HAVE_SKLEARN = True
except ImportError:
    _HAVE_SKLEARN = False


def _best_excerpt(doc: str, query: str, max_len: int = 1500) -> str:
    """Return a window around the highest-density query-term region."""
    if len(doc) <= max_len:
        return doc.strip()
    terms = [t.lower() for t in query.split() if len(t) > 2]
    if not terms:
        return doc[:max_len].strip()
    dl = doc.lower()
    best_pos, best_hits = 0, -1
    step = max(1, max_len // 4)
    for start in range(0, max(1, len(doc) - max_len + 1), step):
        window = dl[start : start + max_len]
        hits = sum(window.count(t) for t in terms)
        if hits > best_hits:
            best_hits = hits
            best_pos = start
    return doc[best_pos : best_pos + max_len].strip()


class LocalIndex:
    """Build a TF-IDF (or keyword-overlap) index over a directory of .txt files."""

    def __init__(self, sources_dir: str) -> None:
        self._sources_dir = Path(sources_dir)
        self._names: List[str] = []
        self._docs: List[str] = []
        self._vectorizer = None
        self._matrix = None
        self._load()

    # ------------------------------------------------------------------
    def _load(self) -> None:
        if not self._sources_dir.exists():
            return
        for p in sorted(self._sources_dir.glob("*.txt")):
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
                self._names.append(p.name)
                self._docs.append(text)
            except Exception:
                continue

        if _HAVE_SKLEARN and self._docs:
            try:
                self._vectorizer = TfidfVectorizer(
                    stop_words="english",
                    ngram_range=(1, 2),
                    max_features=50_000,
                )
                self._matrix = self._vectorizer.fit_transform(self._docs)
            except Exception:
                self._vectorizer = None
                self._matrix = None

    # ------------------------------------------------------------------
    def search(self, query: str, k: int = 2) -> List[Dict]:
        """Return top-*k* hits as ``[{source, score, excerpt}]``."""
        if not self._docs:
            return []

        scores: List[float]
        if self._vectorizer is not None and self._matrix is not None:
            qv = self._vectorizer.transform([query])
            sims = cosine_similarity(qv, self._matrix)[0]
            scores = [float(s) for s in sims]
        else:
            # Keyword-overlap fallback
            q_terms = {t.lower() for t in query.split() if len(t) > 2}
            scores = []
            for doc in self._docs:
                dl = doc.lower()
                scores.append(float(sum(dl.count(t) for t in q_terms)))

        ranked = sorted(range(len(self._docs)), key=lambda i: scores[i], reverse=True)[
            :k
        ]
        results: List[Dict] = []
        for i in ranked:
            if scores[i] <= 0:
                continue
            results.append(
                {
                    "source": self._names[i],
                    "score": round(scores[i], 4),
                    "excerpt": _best_excerpt(self._docs[i], query, 1500),
                }
            )
        return results
