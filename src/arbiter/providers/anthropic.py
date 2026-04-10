"""Anthropic (Claude) provider."""

from __future__ import annotations

import json
import logging
import os
import re



from arbiter.config import ProviderConfig
from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseProvider):
    """Provider backed by the Anthropic Messages API."""

    def _init_client(self, config: ProviderConfig) -> None:
        import anthropic

        api_key = config.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "Anthropic API key not found. Set 'api_key' in provider config "
                "or the ANTHROPIC_API_KEY environment variable."
            )

        self._client = anthropic.Anthropic(
            api_key=api_key,
            timeout=config.timeout,
        )

    # ── plain text call ───────────────────────────────────────────────

    def _call_impl(self, system: str, user: str, max_tokens: int = 4000) -> str:
        kwargs: dict = dict(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )

        # Extended thinking support
        if self.config.thinking:
            thinking_type = self.config.thinking.get("type", "adaptive")
            if thinking_type == "adaptive":
                # Adaptive thinking: no budget_tokens, model decides
                kwargs["thinking"] = {"type": "adaptive"}
                kwargs["max_tokens"] = max_tokens + 16000  # room for thinking
            else:
                # Explicit budget (legacy "enabled" mode)
                budget = self.config.thinking.get("budget_tokens", 8000)
                kwargs["thinking"] = {"type": thinking_type, "budget_tokens": budget}
                kwargs["max_tokens"] = max_tokens + budget

        resp = self._client.messages.create(**kwargs)
        text = "\n".join(
            b.text for b in resp.content if b.type == "text"
        ).strip()
        return text

    # ── structured (JSON) call ────────────────────────────────────────

    def _call_structured_impl(
        self, system: str, user: str, schema: dict, max_tokens: int = 4000
    ) -> dict:
        augmented_system = (
            f"{system}\n\nYou MUST respond with valid JSON matching this schema:\n"
            f"```json\n{json.dumps(schema, indent=2)}\n```"
        )
        raw = self._call_impl(augmented_system, user, max_tokens)

        # Try to extract JSON from the response
        parsed = self._extract_json(raw)
        if parsed is not None:
            return parsed

        # Fallback: try aggressive regex extraction before reaching for OpenAI
        parsed = self._extract_json_aggressive(raw)
        if parsed is not None:
            logger.info("Recovered JSON via aggressive regex extraction")
            return parsed

        # Last resort: ask OpenAI to reformat (may not be installed)
        try:
            logger.warning(
                "Anthropic JSON extraction failed; falling back to OpenAI reformat"
            )
            return self._openai_reformat(raw, schema)
        except ImportError:
            raise ValueError(
                "Anthropic returned non-JSON and the OpenAI package is not "
                "installed for the reformat fallback. Install it with "
                "'pip install openai' or set OPENAI_API_KEY, or retry the "
                "request. Raw response (first 500 chars):\n" + raw[:500]
            ) from None
        except Exception as exc:
            raise ValueError(
                f"Anthropic returned non-JSON and the OpenAI reformat "
                f"fallback also failed ({type(exc).__name__}: {exc}). "
                f"Raw response (first 500 chars):\n{raw[:500]}"
            ) from exc

    # ── helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _extract_json(text: str) -> dict | None:
        """Try to pull a JSON object out of *text*."""
        # Try fenced code block first
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
        # Try raw braces
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        return None

    @staticmethod
    def _extract_json_aggressive(text: str) -> dict | None:
        """Harder regex attempts: strip markdown, find outermost braces."""
        # Strip common markdown wrapping
        cleaned = re.sub(r"^```\w*\n?", "", text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned.strip(), flags=re.MULTILINE)

        # Find the outermost { ... } by tracking brace depth
        start = cleaned.find("{")
        if start == -1:
            return None
        depth = 0
        for i in range(start, len(cleaned)):
            if cleaned[i] == "{":
                depth += 1
            elif cleaned[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(cleaned[start : i + 1])
                    except json.JSONDecodeError:
                        break
        return None

    @staticmethod
    def _openai_reformat(raw: str, schema: dict) -> dict:
        """Use OpenAI to coerce *raw* into the desired JSON schema."""
        import openai

        client = openai.OpenAI(timeout=60)
        resp = client.responses.create(
            model="gpt-5.4-nano",  # cheapest model, sufficient for JSON reformatting
            input=[
                {
                    "role": "system",
                    "content": (
                        "Reformat the following text into valid JSON matching "
                        "the provided schema. Output ONLY the JSON object."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Schema:\n{json.dumps(schema, indent=2)}\n\n"
                        f"Text:\n{raw}"
                    ),
                },
            ],
            text={"format": {"type": "json_schema", "name": "reformat", "schema": schema}},
        )
        return json.loads(resp.output_text)
