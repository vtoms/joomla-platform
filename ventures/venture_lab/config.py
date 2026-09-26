"""Settings, model routing and API cost accounting."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# USD per 1M tokens (input, output). Anthropic first-party list prices.
MODEL_PRICING: dict[str, tuple[float, float]] = {
    "claude-fable-5-1": (10.00, 50.00),
    "claude-opus-5-5": (4.00, 20.00),
    "claude-opus-5": (5.00, 25.00),
    "claude-sonnet-5": (2.00, 10.00),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
}
CACHE_WRITE_MULTIPLIER = 1.25  # 5-minute TTL writes
CACHE_READ_MULTIPLIER = 0.10
BATCH_DISCOUNT = 0.50
WEB_SEARCH_USD_PER_1K = 10.00

# Models that take `thinking: {"type": "adaptive"}` and `output_config.effort`.
ADAPTIVE_THINKING_MODELS = {
    "claude-fable-5-1",
    "claude-opus-5-5",
    "claude-opus-5",
    "claude-sonnet-5",
    "claude-sonnet-4-6",
}
# Models that support the server-side refusal fallback (`fallbacks: "default"`).
SERVER_FALLBACK_MODELS = {"claude-fable-5-1", "claude-opus-5-5", "claude-opus-5"}
SERVER_FALLBACK_BETA = "server-side-fallback-2026-07-01"


def _get(obj: Any, name: str, default: Any = 0) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default) or default
    return getattr(obj, name, default) or default


def usage_cost_usd(model: str, usage: Any, *, batch: bool = False) -> float:
    """Dollar cost of one response's `usage` block."""
    in_price, out_price = MODEL_PRICING.get(model, MODEL_PRICING["claude-opus-5"])
    uncached = _get(usage, "input_tokens")
    cache_write = _get(usage, "cache_creation_input_tokens")
    cache_read = _get(usage, "cache_read_input_tokens")
    output = _get(usage, "output_tokens")
    cost = (
        uncached * in_price
        + cache_write * in_price * CACHE_WRITE_MULTIPLIER
        + cache_read * in_price * CACHE_READ_MULTIPLIER
        + output * out_price
    ) / 1_000_000
    if batch:
        cost *= BATCH_DISCOUNT
    searches = _get(_get(usage, "server_tool_use", None), "web_search_requests")
    cost += searches * WEB_SEARCH_USD_PER_1K / 1000
    return round(cost, 6)


@dataclass
class ModelTiers:
    """Dynamic model routing: strategy on the strongest model, drafting on a
    mid-tier model, bulk classification/extraction on the cheapest one."""

    strategist: str = "claude-opus-5"
    worker: str = "claude-sonnet-5"
    bulk: str = "claude-haiku-4-5"

    def resolve(self, tier_or_model: str) -> str:
        return getattr(self, tier_or_model, tier_or_model)


@dataclass
class ExperimentSettings:
    status: str | None = None  # overrides the catalog default when set
    api_budget_usd_month: float | None = None
    model: str | None = None  # tier name or explicit model id
    effort: str | None = None


@dataclass
class SubscriptionSettings:
    """Run agent sessions through Claude Code (`claude -p`) on a Pro/Max plan instead of API credits."""

    claude_bin: str = "claude"
    cli: str = "venture-lab"  # how the agent invokes this package's CLI
    model: str = ""  # empty = Claude Code's default for your plan
    max_turns: int = 40
    max_sessions_per_tick: int = 3  # protects your plan's usage limits
    permission_mode: str = "dontAsk"
    timeout_minutes: int = 30


@dataclass
class Settings:
    home: Path
    models: ModelTiers = field(default_factory=ModelTiers)
    global_api_budget_usd_month: float = 250.0
    max_iterations_per_run: int = 25
    web_search_max_uses: int = 8
    auto_approve: list[str] = field(default_factory=list)
    webhook_url: str = ""
    experiments: dict[str, ExperimentSettings] = field(default_factory=dict)
    backend: str = "api"  # api | claude-code
    subscription: SubscriptionSettings = field(default_factory=SubscriptionSettings)
    config_path: Path | None = None

    @property
    def db_path(self) -> Path:
        return self.home / "ledger.sqlite3"

    @property
    def artifacts_dir(self) -> Path:
        return self.home / "artifacts"

    def for_experiment(self, experiment_id: str) -> ExperimentSettings:
        return self.experiments.get(experiment_id, ExperimentSettings())


def load_settings(path: str | os.PathLike[str] | None = None) -> Settings:
    """Load settings from TOML (default: $VENTURES_CONFIG or ./venture_lab.toml)."""
    path = Path(path or os.environ.get("VENTURES_CONFIG", "venture_lab.toml"))
    raw: dict[str, Any] = {}
    if path.exists():
        raw = tomllib.loads(path.read_text())

    home = Path(os.environ.get("VENTURES_HOME") or raw.get("home") or "var").expanduser()
    budget = raw.get("budget", {})
    runs = raw.get("runs", {})
    approvals = raw.get("approvals", {})
    settings = Settings(
        home=home,
        models=ModelTiers(**raw.get("models", {})),
        global_api_budget_usd_month=float(budget.get("global_api_usd_month", 250.0)),
        max_iterations_per_run=int(runs.get("max_iterations", 25)),
        web_search_max_uses=int(runs.get("web_search_max_uses", 8)),
        auto_approve=list(approvals.get("auto_approve", [])),
        webhook_url=str(approvals.get("webhook_url", "")),
        experiments={key: ExperimentSettings(**value) for key, value in raw.get("experiments", {}).items()},
        backend=str(raw.get("backend", "api")),
        subscription=SubscriptionSettings(**raw.get("subscription", {})),
        config_path=path if path.exists() else None,
    )
    if settings.backend not in {"api", "claude-code"}:
        raise ValueError(f"backend must be 'api' or 'claude-code', not {settings.backend!r}")
    settings.home.mkdir(parents=True, exist_ok=True)
    settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
    return settings
