from __future__ import annotations

import asyncio
import sys
from collections.abc import AsyncIterator
from copy import deepcopy
from typing import Any
from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel

from agent_runtime.core.bus.events import ToolCallFailedEvent, ToolCallFinishedEvent
from agent_runtime.core.context import ExecutionContext
from agent_runtime.core.events.bus import EventBus
from agent_runtime.core.llm.types import LlmResponse, ToolCallBlock
from agent_runtime.core.loop import AgentLoop
from agent_runtime.core.mcp.client import McpClient, McpToolError
from agent_runtime.core.mcp.tool import McpTool
from agent_runtime.core.tools import invocation
from agent_runtime.core.tools.registry import ToolRegistry

# Exercise the actual stdio JSON-RPC boundary, including initialization and discovery.
_SERVER = r"""
import json
import sys

initialized = False
for line in sys.stdin:
    request = json.loads(line)
    method = request["method"]
    if method == "notifications/initialized":
        initialized = True
        continue
    response = {"jsonrpc": "2.0", "id": request["id"]}
    if method == "initialize":
        response["result"] = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "regression", "version": "1"},
        }
    elif method == "tools/list":
        assert initialized
        response["result"] = {"tools": [{
            "name": "echo", "description": "Return a configured result",
            "inputSchema": {"type": "object", "properties": {}},
        }]}
    elif method == "tools/call":
        assert initialized
        arguments = request["params"]["arguments"]
        if arguments.get("rpc_error"):
            response["error"] = {"code": -32602, "message": "invalid arguments"}
        else:
            response["result"] = arguments
    else:
        raise AssertionError(method)
    print(json.dumps(response), flush=True)
"""


@pytest.fixture
async def mcp_tool() -> AsyncIterator[McpTool]:
    client = McpClient()
    try:
        async with asyncio.timeout(5):
            await client.connect_stdio(sys.executable, ["-u", "-c", _SERVER])
            definitions = await client.list_tools()
        assert [definition.name for definition in definitions] == ["echo"]
        yield McpTool(client, "regression", definitions[0])
    finally:
        await client.close()


@pytest.mark.parametrize(
    ("response", "is_error", "text"),
    [
        (
            {
                "isError": True,
                "content": [
                    {"type": "text", "text": "failed"},
                    {"type": "text", "text": "try another input"},
                ],
            },
            True,
            "failed\ntry another input",
        ),
        ({"isError": True, "content": []}, True, "MCP tool returned isError=true"),
        ({"isError": False, "content": [{"type": "text", "text": "ok"}]}, False, "ok"),
        ({"content": [{"type": "text", "text": "legacy success"}]}, False, "legacy success"),
        ({"rpc_error": True}, True, "invalid arguments (code=-32602)"),
    ],
    ids=["tool-error", "empty-error", "explicit-success", "implicit-success", "rpc-error"],
)
async def test_protocol_result_preserves_error_semantics(
    mcp_tool: McpTool, response: dict[str, object], is_error: bool, text: str
) -> None:
    result = await asyncio.wait_for(mcp_tool.invoke(response), timeout=5)
    assert result.is_error is is_error
    assert result.error_type == ("runtime_error" if is_error else None)
    assert text in result.content
    if not is_error:
        assert result.content == text

    # An application error must not poison the transport or later successful calls.
    subsequent = await mcp_tool.invoke({"content": [{"type": "text", "text": "recovered"}]})
    assert subsequent.content == "recovered"
    assert not subsequent.is_error


async def test_client_raises_tool_error_for_error_result(mcp_tool: McpTool) -> None:
    with pytest.raises(McpToolError, match="execution failed"):
        await mcp_tool._client.call_tool(
            "echo", {"isError": True, "content": [{"type": "text", "text": "execution failed"}]}
        )


async def test_mcp_error_reaches_events_and_next_agent_step(
    mcp_tool: McpTool, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(invocation, "_RETRY_BASE_S", 0)
    registry = ToolRegistry()
    registry.register(mcp_tool)
    bus = EventBus()
    events: list[BaseModel] = []

    async def collect(event: BaseModel) -> None:
        events.append(event)

    bus.subscribe(collect)
    calls: list[list[dict[str, Any]]] = []

    async def chat(**kwargs: Any) -> LlmResponse:
        calls.append(deepcopy(kwargs["messages"]))
        if len(calls) == 1:
            return LlmResponse(
                stop_reason="tool_use",
                tool_calls=[
                    ToolCallBlock(
                        id="call-error",
                        name=mcp_tool.name,
                        input={
                            "isError": True,
                            "content": [{"type": "text", "text": "execution failed"}],
                        },
                    )
                ],
            )
        return LlmResponse(stop_reason="end_turn", text="error handled")

    provider = AsyncMock()
    provider.chat.side_effect = chat
    context = ExecutionContext(run_id="mcp-error", goal="test", max_steps=2)
    await asyncio.wait_for(AgentLoop(provider, registry, bus).run(context), timeout=5)

    failures = [event for event in events if isinstance(event, ToolCallFailedEvent)]
    assert failures
    assert all(event.error_class == "runtime_error" for event in failures)
    assert all("execution failed" in event.error_message for event in failures)
    assert all(event.tool_use_id == "call-error" for event in failures)
    assert not any(isinstance(event, ToolCallFinishedEvent) for event in events)
    assert len(calls) == 2
    block = calls[1][-1]["content"][0]
    assert block["tool_use_id"] == "call-error"
    assert block["is_error"] is True
    assert "execution failed" in block["content"]
    assert context.status == "success"
