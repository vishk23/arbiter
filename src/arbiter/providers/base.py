"""Abstract base class for LLM providers."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod

from arbiter.config import ProviderConfig

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """Common interface every LLM provider must implement."""

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config
        self.model = config.model
        self._init_client(config)

    @abstractmethod
    def _init_client(self, config: ProviderConfig) -> None:
        """Instantiate the vendor SDK client."""

    @abstractmethod
    def call(self, system: str, user: str, max_tokens: int = 4000) -> str:
        """Single LLM call. Must return a non-empty string."""

    @abstractmethod
    def call_structured(
        self, system: str, user: str, schema: dict, max_tokens: int = 4000
    ) -> dict:
        """LLM call that returns a JSON dict conforming to *schema*."""

    def call_with_retry(
        self, system: str, user: str, max_tokens: int = 4000
    ) -> str:
        """Wrap :meth:`call` with exponential-backoff retry.

        Makes up to ``config.max_retries`` attempts (default 6).
        Back-off: 1 s, 2 s, 4 s, 8 s, 16 s, 32 s (capped at 60 s).
        """
        max_tries = self.config.max_retries
        last_err: Exception | None = None
        for attempt in range(max_tries):
            try:
                return self.call(system, user, max_tokens)
            except Exception as exc:
                last_err = exc
                sleep = min(60, 2**attempt)
                logger.warning(
                    "[retry:%s] attempt %d/%d failed: %s: %s -- sleeping %ds",
                    self.__class__.__name__,
                    attempt + 1,
                    max_tries,
                    type(exc).__name__,
                    str(exc)[:120],
                    sleep,
                )
                time.sleep(sleep)
        raise last_err  # type: ignore[misc]
