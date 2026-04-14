"""Multi-provider judge panel."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from jinja2 import Template

from arbiter.config import JudgeConfig, TokenBudgets
from arbiter.judge.aggregator import aggregate
from arbiter.judge.rubric import build_verdict_models, rubric_description

if TYPE_CHECKING:
    from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)
_B = TokenBudgets()

MIN_JUDGES_FOR_VERDICT = 1  # 1 for single-provider setups; 2+ recommended


class JudgePanel:
    """Score a debate transcript using multiple LLM judges.

    Each judge receives the same rubric prompt + transcript and returns
    a structured Verdict.  Results are aggregated; any criterion whose
    spread across judges exceeds ``config.spread_threshold`` is flagged
    as low-confidence.
    """

    def __init__(
        self,
        config: JudgeConfig,
        providers: dict[str, "BaseProvider"],
    ) -> None:
        self.config = config
        self.providers = providers  # {panel_member.provider: BaseProvider}
        self._criteria_ids = [c.id for c in config.rubric]

        _, self._Verdict = build_verdict_models(
            config.rubric, config.sides, config.verdict_options
        )
        self._verdict_schema = self._Verdict.model_json_schema()
        self._rubric_text = rubric_description(config.rubric)

    # ------------------------------------------------------------------ #

    def _render_system(self, topic_name: str = "") -> str:
        """Render the Jinja2 system prompt from config."""
        tpl = Template(self.config.system_prompt)
        return tpl.render(
            topic_name=topic_name,
            rubric_description=self._rubric_text,
        )

    def _build_user_prompt(self, transcript: str) -> str:
        return (
            "You are judging a debate. Below is the full transcript.\n\n"
            f"{self._rubric_text}\n\n"
            f"verdict must be one of: {', '.join(repr(v) for v in self.config.verdict_options)}.\n\n"
            "TRANSCRIPT:\n"
            "================================================================\n"
            f"{transcript}\n"
            "================================================================\n\n"
            "Emit your verdict as STRICT JSON matching the schema. No commentary."
        )

    # ------------------------------------------------------------------ #

    def judge(self, transcript: str, topic_name: str = "") -> dict:
        """Run all panel judges and return aggregated result.

        Parameters
        ----------
        transcript:
            Full debate transcript text.
        topic_name:
            Substituted into the system prompt template.

        Returns
        -------
        dict with keys: per_judge, criterion_means, criterion_spreads,
        low_confidence_flags, verdict_counts, panel_verdict.
        """
        system = self._render_system(topic_name)
        user = self._build_user_prompt(transcript)

        # Run all judges in parallel — they are independent
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def _judge_one(member_provider: str) -> tuple[str, dict | None]:
            provider = self.providers.get(member_provider)
            if provider is None:
                logger.error("No provider for panel member '%s'", member_provider)
                return member_provider, None
            try:
                # Pass Pydantic class directly (not dict schema) so providers
                # can use native structured output with thinking enabled.
                raw = provider.call_structured(
                    system=system,
                    user=user,
                    schema=self._Verdict,
                    max_tokens=_B.xl,
                )
                parsed = self._Verdict.model_validate(raw)
                logger.info("Judge %s -> verdict=%s", member_provider, raw.get("verdict", "?"))
                return member_provider, parsed.model_dump()
            except Exception:
                logger.exception("Judge '%s' failed", member_provider)
                return member_provider, None

        verdicts: dict[str, dict] = {}
        with ThreadPoolExecutor(max_workers=len(self.config.panel)) as pool:
            futures = [pool.submit(_judge_one, m.provider) for m in self.config.panel]
            for fut in as_completed(futures):
                name, result = fut.result()
                if result is not None:
                    verdicts[name] = result

        if len(verdicts) < MIN_JUDGES_FOR_VERDICT:
            raise RuntimeError(
                f"Only {len(verdicts)} judge(s) succeeded; "
                f"need at least {MIN_JUDGES_FOR_VERDICT}"
            )

        return aggregate(
            verdicts,
            criteria_names=self._criteria_ids,
            sides=self.config.sides,
            spread_threshold=self.config.spread_threshold,
        )
