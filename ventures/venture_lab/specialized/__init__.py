"""Experiment-specific tools, looked up by name from `Experiment.extra_tools`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from venture_lab.specialized.economics import unit_economics_tool
from venture_lab.specialized.extraction import extraction_tools
from venture_lab.specialized.voice import voice_spec_tool

Factory = Callable[..., list[Any]]

REGISTRY: dict[str, Factory] = {
    "voice_agent_spec": lambda **kw: [voice_spec_tool(kw["workspace"])],
    "unit_economics": lambda **kw: [unit_economics_tool()],
    "batch_extraction": lambda **kw: extraction_tools(**kw),
}


def extra_tools(
    names: tuple[str, ...],
    experiment_id: str,
    ledger: Any,
    workspace: Any,
    client: Any,
    settings: Any,
    api_budget_usd: float,
) -> list[Any]:
    tools: list[Any] = []
    for name in names:
        if name not in REGISTRY:
            raise KeyError(f"unknown specialized tool set {name!r}")
        tools += REGISTRY[name](
            experiment_id=experiment_id,
            ledger=ledger,
            workspace=workspace,
            client=client,
            settings=settings,
            api_budget_usd=api_budget_usd,
        )
    return tools
