from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest
from openai import AsyncOpenAI

from agent_runtime.core.app import CoreApp
from agent_runtime.core.config import RuntimeConfig, get_config
from agent_runtime.core.events.bus import EventBus
from agent_runtime.core.llm import openai_provider
from agent_runtime.core.llm.factory import create_provider
from agent_runtime.core.llm.provider import AnthropicProvider
from agent_runtime.core.runner import AgentRunner


def _chunk(delta: dict, finish: str | None = None) -> dict:
    return {"choices": [{"index": 0, "delta": delta, "finish_reason": finish}]}


def _mock_api(monkeypatch, *turns: list[dict]) -> list[dict]:
    requests: list[dict] = []
    responses = iter(turns)

    def handle(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://example.test/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer test-key"
        requests.append(json.loads(request.content))
        data = "".join(f"data: {json.dumps(chunk)}\n\n" for chunk in next(responses))
        return httpx.Response(
            200, headers={"Content-Type": "text/event-stream"}, text=data + "data: [DONE]\n\n"
        )

    def client(**kwargs: Any) -> AsyncOpenAI:
        return AsyncOpenAI(
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(handle)), **kwargs
        )

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1")
    monkeypatch.setattr(openai_provider, "AsyncOpenAI", client)
    return requests


@pytest.mark.parametrize("engine", ["loop", pytest.param("graph", marks=pytest.mark.graph)])
async def test_runner_gpt_parallel_tools_and_usage(tmp_path, monkeypatch, engine):
    if engine == "graph":
        pytest.importorskip("langgraph.graph")
    requests = _mock_api(
        monkeypatch,
        [
            _chunk(
                {
                    "tool_calls": [
                        {
                            "index": 0,
                            "id": "a",
                            "type": "function",
                            "function": {"name": "task_list", "arguments": "{"},
                        },
                        {
                            "index": 1,
                            "id": "b",
                            "type": "function",
                            "function": {"name": "task_get", "arguments": '{"task_id":'},
                        },
                    ]
                }
            ),
            _chunk(
                {
                    "tool_calls": [
                        {"index": 1, "function": {"arguments": "7}"}},
                        {"index": 0, "function": {"arguments": "}"}},
                    ]
                },
                "tool_calls",
            ),
        ],
        [
            _chunk({"content": "all "}),
            _chunk({"content": "done"}, "stop"),
            {
                "choices": [],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 6,
                    "total_tokens": 106,
                    "prompt_tokens_details": {"cached_tokens": 20},
                },
            },
        ],
    )
    config = RuntimeConfig()
    config.agent.engine = engine
    config.llm.provider = "openai"
    events = []

    async def collect(event):
        events.append(event)

    result = await AgentRunner(config, runs_dir=tmp_path, extra_handlers=[collect]).run_and_capture(
        "test"
    )
    assert result.status == "success"
    assert [e.token for e in events if e.type == "llm.token"] == ["all ", "done"]
    (usage,) = [e for e in events if e.type == "llm.usage"]
    assert (usage.input_tokens, usage.cache_read_input_tokens, usage.output_tokens) == (80, 20, 6)
    first, second = requests
    assert first["model"] == "gpt-4.1-mini"
    assert first["messages"][0]["role"] == "system"
    assert first["stream"] and first["stream_options"] == {"include_usage": True}
    assert any(
        tool["function"]["name"] == "task_list" and "parameters" in tool["function"]
        for tool in first["tools"]
    )
    assistant, result_a, result_b = second["messages"][-3:]
    assert [c["id"] for c in assistant["tool_calls"]] == ["a", "b"]
    assert json.loads(assistant["tool_calls"][1]["function"]["arguments"]) == {"task_id": 7}
    assert result_a["role"] == result_b["role"] == "tool"
    assert result_a["tool_call_id"] == "a" and result_b["tool_call_id"] == "b"
    assert result_b["content"].startswith("Error:")


@pytest.mark.parametrize("finish", ["length", "tool_calls", None, "content_filter"])
async def test_incomplete_call_never_executes(finish, monkeypatch):
    requests = _mock_api(
        monkeypatch,
        [
            _chunk(
                {
                    "tool_calls": [
                        {
                            "index": 0,
                            "type": "function",
                            "id": "a",
                            "function": {"name": "task_get", "arguments": "{"},
                        }
                    ]
                },
                finish,
            )
        ],
    )
    config = RuntimeConfig()
    config.llm.provider = "openai"
    provider = CoreApp()._provider_for_compaction(config)
    call = provider.chat(
        [{"role": "user", "content": "test"}], [], EventBus(), "r", system="summarize"
    )
    if finish == "length":
        response = await call
        assert response.stop_reason == "max_tokens"
        assert response.tool_calls[0].input == {}
    else:
        with pytest.raises(ValueError):
            await call
    assert "tools" not in requests[0]
    assert requests[0]["messages"][0] == {"role": "system", "content": "summarize"}


def test_provider_configuration(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "config.toml"
    path.write_text('[llm]\nprovider="openai"\n')
    monkeypatch.setenv("AGENTRT_CONFIG", str(path))
    monkeypatch.delenv("AGENTRT_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("AGENTRT_LLM_DEFAULT_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    config = get_config()
    assert config.llm.model == "gpt-4.1-mini"
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        create_provider(config.llm)
    monkeypatch.setenv("AGENTRT_LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("AGENTRT_LLM_DEFAULT_MODEL", "deepseek-flash")
    config = get_config()
    assert config.llm.model == "deepseek-flash"
    assert isinstance(create_provider(config.llm), AnthropicProvider)
    monkeypatch.setenv("AGENTRT_LLM_PROVIDER", "typo")
    with pytest.raises(SystemExit, match="llm.provider"):
        get_config()
