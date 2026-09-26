"""Drives the real SDK tool runner against a local fake API server, to check that
the request we build (tools, server tools, fallbacks, caching) serialises and the
loop executes tools end to end, without an API key or network access."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import anthropic
import pytest

from venture_lab.agent import run_experiment
from venture_lab.experiments import get

RESPONSES = [
    {
        "content": [
            {
                "type": "tool_use",
                "id": "toolu_1",
                "name": "save_artifact",
                "input": {"path": "notes/plan.md", "content": "# Plan"},
            },
        ],
        "stop_reason": "tool_use",
    },
    {"content": [{"type": "text", "text": "DONE: notes/plan.md"}], "stop_reason": "end_turn"},
]


@pytest.fixture
def fake_api(monkeypatch):
    for var in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy", "ALL_PROXY", "all_proxy"):
        monkeypatch.delenv(var, raising=False)
    requests: list[dict] = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append({"path": self.path, "body": body, "beta": self.headers.get("anthropic-beta", "")})
            canned = RESPONSES[min(len(requests) - 1, len(RESPONSES) - 1)]
            payload = {
                "id": f"msg_{len(requests)}",
                "type": "message",
                "role": "assistant",
                "model": body["model"],
                "stop_sequence": None,
                "usage": {
                    "input_tokens": 1200,
                    "output_tokens": 300,
                    "cache_read_input_tokens": 0,
                    "cache_creation_input_tokens": 900,
                },
                **canned,
            }
            data = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}", requests
    server.shutdown()


def test_real_sdk_request_shape(settings, ledger, fake_api):
    base_url, requests = fake_api
    client = anthropic.Anthropic(api_key="test", base_url=base_url, max_retries=0)
    run = run_experiment(get("voice-receptionist"), settings, ledger, client=client)

    assert run["status"] == "ok" and run["summary"] == "DONE: notes/plan.md"
    assert run["cost_usd"] > 0
    assert len(requests) == 2
    first = requests[0]
    assert first["path"].startswith("/v1/messages")
    assert "server-side-fallback-2026-07-01" in first["beta"]
    body = first["body"]
    assert body["fallbacks"] == "default"
    assert body["thinking"] == {"type": "adaptive"}
    assert body["system"][-1]["cache_control"] == {"type": "ephemeral"}
    names = {t["name"] for t in body["tools"]}
    assert {
        "save_artifact",
        "request_action",
        "build_voice_agent_spec",
        "calculate_unit_economics",
        "web_search",
        "web_fetch",
    } <= names
    # Second request carries the tool result from actually running save_artifact.
    last_user = requests[1]["body"]["messages"][-1]
    assert last_user["content"][0]["type"] == "tool_result"
    assert (settings.artifacts_dir / "voice-receptionist" / "notes" / "plan.md").read_text() == "# Plan"
