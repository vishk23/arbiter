"""Abstract base class for LLM providers."""

from __future__ import annotations

import json as _json
import logging
import time
from abc import ABC, abstractmethod

from pydantic import BaseModel

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
        logger.info("Calling %s (%s)...", label, self.model)
        t0 = time.time()
        result = self._call_impl(system, user, max_tokens)
        elapsed = time.time() - t0
        logger.info("Response received (%d chars, %.1fs)", len(result), elapsed)
        return result

    def call_structured(
        self,
        system: str,
        user: str,
        schema: dict | type[BaseModel],
        max_tokens: int = 4000,
    ) -> dict:
        label = self._provider_label()
        logger.info("Calling %s (%s) [structured]...", label, self.model)
        t0 = time.time()

        if isinstance(schema, type) and issubclass(schema, BaseModel):
            result = self._call_parsed_impl(system, user, schema, max_tokens)
        else:
            result = self._call_structured_impl(system, user, schema, max_tokens)

        elapsed = time.time() - t0
        chars = len(_json.dumps(result))
        logger.info("Response received (%d chars, %.1fs)", chars, elapsed)
        return result

    def _call_parsed_impl(
        self,
        system: str,
        user: str,
        model_class: type[BaseModel],
        max_tokens: int = 4000,
    ) -> dict:
        """Default: convert Pydantic model to dict schema, call _call_structured_impl, validate."""
        schema_dict = model_class.model_json_schema()
        result = self._call_structured_impl(system, user, schema_dict, max_tokens)
        validated = model_class.model_validate(result)
        return validated.model_dump()

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
