"""Agent wrapper -- binds a name + config to a provider."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arbiter.config import AgentConfig
    from arbiter.providers.base import BaseProvider


class Agent:
    """A named debate participant backed by an LLM provider.

    Parameters
    ----------
    name:
        Display name used in transcripts and the ledger (e.g. "Proponent").
    config:
        Agent-level settings (side, system prompt, max_words, adversarial).
    provider:
        Resolved :class:`BaseProvider` instance for this agent.
    """

    def __init__(
        self,
        name: str,
        config: "AgentConfig",
        provider: "BaseProvider",
    ) -> None:
        self.name = name
        self.config = config
        self.provider = provider

    # ------------------------------------------------------------------ #

    def call(self, system: str, user: str) -> str:
        """Invoke the underlying provider with exponential-backoff retry."""
        return self.provider.call_with_retry(system, user, self.config.max_words * 6)

    # ------------------------------------------------------------------ #

    @property
    def side(self) -> str:
        """Which side this agent argues for (e.g. 'Proponent', 'Skeptic')."""
        return self.config.side

    @property
    def is_adversarial(self) -> bool:
        """True if this agent is in red-team / adversarial mode."""
        return self.config.adversarial

    @property
    def system_prompt(self) -> str:
        """The raw (pre-template) system prompt from config."""
        return self.config.system_prompt

    @property
    def max_words(self) -> int:
        return self.config.max_words
