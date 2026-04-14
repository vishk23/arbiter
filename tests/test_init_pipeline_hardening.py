"""Tests for init pipeline hardening: fail-loud on 0 claims, provider logging."""



class TestExtractClaimsFailLoud:
    """Verify extract_claims logs properly on empty results."""

    def test_zero_claims_logs_error(self, caplog):
        """When all chunks return 0 claims, an error should be logged."""
        import logging
        from arbiter.init.pdf_reader import extract_claims
        from arbiter.config import ProviderConfig
        from arbiter.providers.base import BaseProvider

        class MockProvider(BaseProvider):
            def _init_client(self, config):
                pass
            def _call_impl(self, system, user, max_tokens=4000):
                return ""
            def _call_structured_impl(self, system, user, schema, max_tokens=4000):
                return {"claims": []}

        config = ProviderConfig(model="test", max_retries=1)
        provider = MockProvider(config)

        with caplog.at_level(logging.ERROR, logger="arbiter.init.pdf_reader"):
            claims = extract_claims("Some document text here.", provider)

        assert claims == []
        assert any("0 claims" in r.message for r in caplog.records)

    def test_nonempty_claims_no_error(self, caplog):
        """When claims are found, no error should be logged."""
        import logging
        from arbiter.init.pdf_reader import extract_claims
        from arbiter.config import ProviderConfig
        from arbiter.providers.base import BaseProvider

        class MockProvider(BaseProvider):
            def _init_client(self, config):
                pass
            def _call_impl(self, system, user, max_tokens=4000):
                return ""
            def _call_structured_impl(self, system, user, schema, max_tokens=4000):
                return {"claims": [
                    {"id": "C1", "claim": "test claim", "category": "logical",
                     "is_formal": False, "depends_on": [], "quote": "", "section": ""}
                ]}

        config = ProviderConfig(model="test", max_retries=1)
        provider = MockProvider(config)

        with caplog.at_level(logging.ERROR, logger="arbiter.init.pdf_reader"):
            claims = extract_claims("Some document text.", provider)

        assert len(claims) == 1
        assert not any("0 claims" in r.message for r in caplog.records
                       if r.levelno >= logging.ERROR)


class TestChunking:
    """Verify PDF text chunking respects limits."""

    def test_small_text_single_chunk(self):
        from arbiter.init.pdf_reader import _chunk_text
        text = "Short text."
        chunks = _chunk_text(text)
        assert len(chunks) == 1

    def test_large_text_splits(self):
        from arbiter.init.pdf_reader import _chunk_text, _MAX_CHUNK_CHARS
        # Create text larger than max chunk
        text = "A" * (_MAX_CHUNK_CHARS + 1000)
        chunks = _chunk_text(text)
        assert len(chunks) >= 2

    def test_heading_split(self):
        from arbiter.init.pdf_reader import _chunk_text
        # Create text with headings that exceeds limit
        sections = [f"\n# Section {i}\n" + "x" * 50000 for i in range(5)]
        text = "".join(sections)
        chunks = _chunk_text(text, max_chars=60000)
        assert len(chunks) >= 2
