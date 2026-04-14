"""Tests for strip_markdown_fences utility."""

from arbiter.providers.base import strip_markdown_fences


class TestStripMarkdownFences:
    def test_plain_json_unchanged(self):
        raw = '{"key": "value"}'
        assert strip_markdown_fences(raw) == '{"key": "value"}'

    def test_strips_json_fence(self):
        raw = '```json\n{"key": "value"}\n```'
        assert strip_markdown_fences(raw) == '{"key": "value"}'

    def test_strips_bare_fence(self):
        raw = '```\n{"key": "value"}\n```'
        assert strip_markdown_fences(raw) == '{"key": "value"}'

    def test_strips_with_trailing_whitespace(self):
        raw = '```json\n{"key": "value"}\n```\n  '
        assert strip_markdown_fences(raw) == '{"key": "value"}'

    def test_preserves_inner_newlines(self):
        raw = '```json\n{\n  "a": 1,\n  "b": 2\n}\n```'
        result = strip_markdown_fences(raw)
        assert '"a": 1' in result
        assert '"b": 2' in result
