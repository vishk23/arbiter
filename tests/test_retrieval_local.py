"""Tests for T30: Retrieval local_index (TF-IDF + fallback)."""

import tempfile
from pathlib import Path

from arbiter.retrieval.local_index import LocalIndex, _best_excerpt


class TestBestExcerpt:
    def test_short_doc_returns_whole(self):
        doc = "Short document."
        assert _best_excerpt(doc, "short") == doc

    def test_long_doc_extracts_window(self):
        # Create a doc longer than max_len=50
        doc = "A " * 100 + "MATCH TARGET HERE " + "B " * 100
        result = _best_excerpt(doc, "MATCH TARGET", max_len=50)
        assert len(result) <= 50
        assert "MATCH" in result or "TARGET" in result

    def test_empty_query_returns_start(self):
        doc = "A" * 3000
        result = _best_excerpt(doc, "", max_len=100)
        assert len(result) <= 100


class TestLocalIndex:
    def test_empty_dir(self):
        with tempfile.TemporaryDirectory() as td:
            index = LocalIndex(td)
            assert index.search("anything") == []

    def test_nonexistent_dir(self):
        index = LocalIndex("/nonexistent/path/to/sources")
        assert index.search("anything") == []

    def test_single_file_search(self):
        with tempfile.TemporaryDirectory() as td:
            Path(td, "doc1.txt").write_text(
                "Consciousness is a fundamental property of matter. "
                "Qualia cannot be reduced to physical processes."
            )
            index = LocalIndex(td)
            results = index.search("consciousness qualia", k=2)
            assert len(results) == 1
            assert results[0]["source"] == "doc1.txt"
            assert results[0]["score"] > 0

    def test_multiple_files_ranking(self):
        with tempfile.TemporaryDirectory() as td:
            Path(td, "relevant.txt").write_text(
                "quantum consciousness quantum consciousness quantum "
                "consciousness explains the hard problem"
            )
            Path(td, "irrelevant.txt").write_text(
                "recipes for chocolate cake and baking instructions"
            )
            index = LocalIndex(td)
            results = index.search("quantum consciousness", k=2)
            assert len(results) >= 1
            assert results[0]["source"] == "relevant.txt"

    def test_k_limits_results(self):
        with tempfile.TemporaryDirectory() as td:
            for i in range(5):
                Path(td, f"doc{i}.txt").write_text(f"document {i} about science")
            index = LocalIndex(td)
            results = index.search("science", k=2)
            assert len(results) <= 2

    def test_result_format(self):
        with tempfile.TemporaryDirectory() as td:
            Path(td, "test.txt").write_text("hello world test content")
            index = LocalIndex(td)
            results = index.search("hello", k=1)
            if results:
                r = results[0]
                assert "source" in r
                assert "score" in r
                assert "excerpt" in r
