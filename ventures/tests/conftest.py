from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest

from venture_lab.config import Settings
from venture_lab.ledger import Ledger


@pytest.fixture
def settings(tmp_path) -> Settings:
    s = Settings(home=tmp_path)
    s.artifacts_dir.mkdir(parents=True, exist_ok=True)
    return s


@pytest.fixture
def ledger(settings) -> Ledger:
    led = Ledger(settings.db_path)
    yield led
    led.close()


def usage(inp: int = 1000, out: int = 500, cache_read: int = 0) -> SimpleNamespace:
    return SimpleNamespace(
        input_tokens=inp,
        output_tokens=out,
        cache_read_input_tokens=cache_read,
        cache_creation_input_tokens=0,
        server_tool_use=None,
    )


def tool_use(tool: str, /, **inp: Any) -> SimpleNamespace:
    return SimpleNamespace(type="tool_use", id=f"tu_{tool}", name=tool, input=inp)


def text(t: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=t)


class FakeRunner:
    """Mimics the SDK tool runner: yields scripted messages and executes the
    tool_use blocks in them with the real tool objects."""

    def __init__(self, script: list[SimpleNamespace], tools: list[Any]):
        self.script = script
        self.tools = {getattr(t, "name", None): t for t in tools if hasattr(t, "call")}
        self.executed: list[tuple[str, str]] = []
        self._last = None

    def __iter__(self):
        for msg in self.script:
            self._last = msg
            yield msg

    def generate_tool_call_response(self):
        blocks = [b for b in self._last.content if b.type == "tool_use"]
        if not blocks:
            return None
        results = []
        for b in blocks:
            out = self.tools[b.name].call(b.input)
            self.executed.append((b.name, out))
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
        return {"role": "user", "content": results}


class FakeClient:
    def __init__(self, script: list[SimpleNamespace]):
        self.script = script
        self.calls: list[dict[str, Any]] = []
        self.runner: FakeRunner | None = None
        self.beta = SimpleNamespace(messages=SimpleNamespace(tool_runner=self._tool_runner))

    def _tool_runner(self, **kwargs: Any) -> FakeRunner:
        self.calls.append(kwargs)
        self.runner = FakeRunner(self.script, kwargs["tools"])
        return self.runner


def message(
    *content: SimpleNamespace, stop_reason: str = "end_turn", u: SimpleNamespace | None = None
) -> SimpleNamespace:
    return SimpleNamespace(content=list(content), stop_reason=stop_reason, usage=u or usage(), model="claude-opus-5")


__all__ = ["FakeClient", "message", "text", "tool_use", "usage", "json"]
