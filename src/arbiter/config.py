"""Pydantic config models + YAML loader for Arbiter."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import yaml
from pydantic import BaseModel, Field, model_validator


# ── Provider ───────────────────────────────────────────────────────────


class ProviderConfig(BaseModel):
    model: str
    max_tokens: int = 4000
    timeout: int = 180
    max_retries: int = 6
    api_key: Optional[str] = None  # env var takes precedence
    base_url: Optional[str] = None  # for Ollama / custom endpoints
    thinking: Optional[Dict[str, Any]] = None  # Anthropic extended thinking
    reasoning: Optional[Dict[str, Any]] = None  # OpenAI reasoning effort
    plugin: Optional[str] = None  # custom provider: "module:ClassName" or "path/file.py:Class"


# ── Agent ──────────────────────────────────────────────────────────────


class AgentConfig(BaseModel):
    provider: str  # key into providers dict
    side: str  # Proponent, Skeptic, Neutral, or custom
    system_prompt: str
    max_words: int = 500
    adversarial: bool = False  # marks red-team agent


# ── Convergence ────────────────────────────────────────────────────────


class ConvergenceConfig(BaseModel):
    max_rounds: int = 6
    no_growth_halt: int = 2  # halt after N rounds without ledger growth


# ── Validity gate ──────────────────────────────────────────────────────


class StipulatedRule(BaseModel):
    id: str
    fact: str
    bad_patterns: List[str]
    denial_patterns: List[str] = []


class EntailmentCheckConfig(BaseModel):
    enabled: bool = True
    provider: str  # which provider runs the check
    effort: str = "high"
    stipulated_facts: List[str] = []  # plain-English facts for the LLM
    system_prompt: Optional[str] = None  # custom entailment prompt


class GateConfig(BaseModel):
    enabled: bool = True
    max_rewrites: int = 2
    extraction_provider: Optional[str] = None  # provider for claim extraction
    stipulated_rules: List[StipulatedRule] = []
    seed_terms: Dict[str, str] = {}
    entailment_check: Optional[EntailmentCheckConfig] = None


# ── Z3 verifier ────────────────────────────────────────────────────────


class Z3Config(BaseModel):
    module: str  # path to Python module exporting verify() -> dict
    stipulation_template: Optional[str] = None  # Jinja2 template for agent injection


# ── Judge ──────────────────────────────────────────────────────────────


class RubricCriterion(BaseModel):
    id: str
    name: str
    description: str
    min_score: int = Field(default=0, alias="min")
    max_score: int = Field(default=10, alias="max")

    model_config = {"populate_by_name": True}


class JudgePanelMember(BaseModel):
    provider: str


class MidDebateConfig(BaseModel):
    enabled: bool = True
    provider: str


class JudgeConfig(BaseModel):
    system_prompt: str = ""
    rubric: List[RubricCriterion]
    sides: List[str] = ["Proponent", "Skeptic"]
    verdict_options: List[str] = ["Proponent", "Skeptic", "Tied"]
    spread_threshold: int = 3
    panel: List[JudgePanelMember]
    mid_debate: Optional[MidDebateConfig] = None


# ── Steelman ───────────────────────────────────────────────────────────


class SteelmanConfig(BaseModel):
    enabled: bool = True
    max_iterations: int = 4
    steelman_provider: str
    critic_provider: str
    judge_provider: str


# ── Retrieval ──────────────────────────────────────────────────────────


class LocalRetrievalConfig(BaseModel):
    sources_dir: str
    k: int = 2


class WebRetrievalConfig(BaseModel):
    provider: str = "tavily"
    k: int = 2


class RetrievalConfig(BaseModel):
    local: Optional[LocalRetrievalConfig] = None
    web: Optional[WebRetrievalConfig] = None


# ── Topic ──────────────────────────────────────────────────────────────


class TopicConfig(BaseModel):
    name: str
    summary: str
    counter_thesis: Optional[str] = None
    privileged_context: Dict[str, str] = {}  # side -> privileged text


# ── Output ─────────────────────────────────────────────────────────────


class OutputConfig(BaseModel):
    dir: str = "output/"
    live_log: bool = True
    formats: List[str] = ["json", "markdown"]
    checkpoint_db: str = "checkpoints.sqlite"


# ── Root config ────────────────────────────────────────────────────────


class ArbiterConfig(BaseModel):
    schema_version: str = "1.0"
    topic: TopicConfig
    topology: Literal["standard", "gated", "adversarial"] = "standard"
    providers: Dict[str, ProviderConfig]
    agents: Dict[str, AgentConfig]
    convergence: ConvergenceConfig = ConvergenceConfig()
    gate: Optional[GateConfig] = None
    z3: Optional[Z3Config] = None
    judge: JudgeConfig
    steelman: Optional[SteelmanConfig] = None
    retrieval: Optional[RetrievalConfig] = None
    output: OutputConfig = OutputConfig()

    @model_validator(mode="after")
    def validate_provider_refs(self) -> "ArbiterConfig":
        """Every agent/judge/gate provider ref must exist in providers dict."""
        for name, agent in self.agents.items():
            if agent.provider not in self.providers:
                raise ValueError(
                    f"Agent '{name}' references undefined provider '{agent.provider}'"
                )
        for member in self.judge.panel:
            if member.provider not in self.providers:
                raise ValueError(
                    f"Judge panel references undefined provider '{member.provider}'"
                )
        if self.gate and self.gate.entailment_check:
            ec = self.gate.entailment_check
            if ec.enabled and ec.provider not in self.providers:
                raise ValueError(
                    f"Entailment check references undefined provider '{ec.provider}'"
                )
        return self

    @model_validator(mode="after")
    def infer_topology(self) -> "ArbiterConfig":
        """Enable gate config automatically for gated/adversarial topologies."""
        if self.topology in ("gated", "adversarial") and self.gate is None:
            self.gate = GateConfig()
        return self


def load_config(path: Path) -> ArbiterConfig:
    """Load and validate a YAML config file. Resolves relative paths."""
    with open(path) as f:
        raw = yaml.safe_load(f)

    config_dir = path.parent

    # Resolve relative paths
    if "z3" in raw and "module" in raw["z3"]:
        p = Path(raw["z3"]["module"])
        if not p.is_absolute():
            raw["z3"]["module"] = str(config_dir / p)

    if "retrieval" in raw and "local" in raw.get("retrieval", {}):
        p = Path(raw["retrieval"]["local"]["sources_dir"])
        if not p.is_absolute():
            raw["retrieval"]["local"]["sources_dir"] = str(config_dir / p)

    if "output" in raw:
        p = Path(raw["output"].get("dir", "output/"))
        if not p.is_absolute():
            raw["output"]["dir"] = str(config_dir / p)
        p = Path(raw["output"].get("checkpoint_db", "checkpoints.sqlite"))
        if not p.is_absolute():
            raw["output"]["checkpoint_db"] = str(config_dir / p)

    return ArbiterConfig.model_validate(raw)
