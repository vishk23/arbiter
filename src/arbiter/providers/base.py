"""Abstract base class for LLM providers."""

from __future__ import annotations

import json as _json
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

    # -- abstract implementation methods (overridden by each provider) ------

    @abstractmethod
    def _call_impl(self, system: str, user: str, max_tokens: int = 4000) -> str:
        """Single LLM call. Must return a non-empty string."""

    @abstractmethod
    def _call_structured_impl(
        self, system: str, user: str, schema: dict, max_tokens: int = 4000
    ) -> dict:
        """LLM call that returns a JSON dict conforming to *schema*."""

    # -- public API (wraps impl methods with logging) ----------------------

    def _provider_label(self) -> str:
        return self.__class__.__name__.replace("Provider", "")

    def call(self, system: str, user: str, max_tokens: int = 4000) -> str:
        label = self._provider_label()
        print(f"  Calling {label} ({self.model})...", flush=True)
        logger.debug("call start: %s %s", label, self.model)
        t0 = time.time()
        result = self._call_impl(system, user, max_tokens)
        elapsed = time.time() - t0
        print(
            f"  Response received ({len(result):,} chars, {elapsed:.1f}s)",
            flush=True,
        )
        logger.debug("call end: %s %s %d chars %.1fs", label, self.model, len(result), elapsed)
        return result

    def call_structured(
        self, system: str, user: str, schema: dict, max_tokens: int = 4000
    ) -> dict:
        label = self._provider_label()
        print(f"  Calling {label} ({self.model}) [structured]...", flush=True)
        logger.debug("call_structured start: %s %s", label, self.model)
        t0 = time.time()
        result = self._call_structured_impl(system, user, schema, max_tokens)
        elapsed = time.time() - t0
        chars = len(_json.dumps(result))
        print(
            f"  Response received ({chars:,} chars, {elapsed:.1f}s)",
            flush=True,
        )
        logger.debug("call_structured end: %s %s %d chars %.1fs", label, self.model, chars, elapsed)
        return result

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
                msg = (
                    f"[retry:{self.__class__.__name__}] "
                    f"attempt {attempt + 1}/{max_tries} failed: "
                    f"{type(exc).__name__}: {str(exc)[:120]} "
                    f"-- sleeping {sleep}s"
                )
                logger.warning(msg)
                print(msg, flush=True)  # always visible to user
                time.sleep(sleep)
        raise last_err  # type: ignore[misc]
