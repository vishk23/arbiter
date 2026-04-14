"""Tests for OpenAI strict mode handling of dynamic-key schemas."""

from arbiter.providers.openai import OpenAIProvider


class TestAdditionalPropertiesPreservation:
    """Verify _add_additional_properties_false preserves intentional additionalProperties."""

    def test_injects_false_when_absent(self):
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        result = OpenAIProvider._add_additional_properties_false(schema)
        assert result["additionalProperties"] is False

    def test_preserves_dict_additional_properties(self):
        """Dynamic-key schema: additionalProperties: {type: string} must survive."""
        schema = {
            "type": "object",
            "additionalProperties": {"type": "string"},
        }
        result = OpenAIProvider._add_additional_properties_false(schema)
        assert result["additionalProperties"] == {"type": "string"}

    def test_preserves_explicit_false(self):
        schema = {"type": "object", "additionalProperties": False}
        result = OpenAIProvider._add_additional_properties_false(schema)
        assert result["additionalProperties"] is False

    def test_preserves_explicit_true(self):
        schema = {"type": "object", "additionalProperties": True}
        result = OpenAIProvider._add_additional_properties_false(schema)
        assert result["additionalProperties"] is True

    def test_nested_objects_still_get_false(self):
        schema = {
            "type": "object",
            "properties": {
                "inner": {
                    "type": "object",
                    "properties": {"x": {"type": "integer"}},
                }
            },
        }
        result = OpenAIProvider._add_additional_properties_false(schema)
        assert result["additionalProperties"] is False
        assert result["properties"]["inner"]["additionalProperties"] is False


class TestHasDynamicKeys:
    def test_detects_dict_additional_properties(self):
        schema = {"type": "object", "additionalProperties": {"type": "string"}}
        assert OpenAIProvider._has_dynamic_keys(schema) is True

    def test_false_for_missing(self):
        schema = {"type": "object"}
        assert OpenAIProvider._has_dynamic_keys(schema) is False

    def test_false_for_boolean(self):
        schema = {"type": "object", "additionalProperties": False}
        assert OpenAIProvider._has_dynamic_keys(schema) is False
