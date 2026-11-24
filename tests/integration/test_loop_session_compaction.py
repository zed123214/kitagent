from pathlib import Path

import pytest

from agent_runtime.core.config import RuntimeConfig
from agent_runtime.core.events.bus import EventBus
from agent_runtime.core.graph.fake_provider import ScriptedProvider
from agent_runtime.core.llm.types import LlmResponse, ToolCallBlock, UsageStats
from agent_runtime.core.runner import AgentRunner
from agent_runtime.core.session.manager import SessionManager
from agent_runtime.core.session.store import SessionStore


@pytest.mark.parametrize("compactions", [1, 2])
async def test_next_turn_replays_history_after_auto_compaction(
    tmp_path: Path, compactions: int
) -> None:
    config = RuntimeConfig()
    config.compaction.auto_threshold = 0.8
    answer = "Report code: K-417"
    follow_up = "What was the report code?"
    tool_ids = [f"list-{i}" for i in range(compactions)]

    class ReportProvider(ScriptedProvider):
        async def chat(self, messages, tool_schemas, bus, run_id, **kwargs):
            if messages[-1]["content"] == follow_up:
                previous = messages[-2]
                reply = "No report code in history"
                if previous["role"] == "assistant":
                    reply = previous["content"][0]["text"].removeprefix("Report code: ")
                return LlmResponse(stop_reason="end_turn", text=reply)
            return await super().chat(messages, tool_schemas, bus, run_id, **kwargs)

    script = [LlmResponse(stop_reason="end_turn", text="Ready")]
    for tool_id in tool_ids:
        script.extend(
            [
                LlmResponse(
                    stop_reason="tool_use",
                    tool_calls=[ToolCallBlock(id=tool_id, name="task_list", input={})],
                    usage=UsageStats(input_tokens=900, output_tokens=10, context_pct=0.9),
                ),
                LlmResponse(stop_reason="end_turn", text="Tasks checked; report pending."),
            ]
        )
    script.append(LlmResponse(stop_reason="end_turn", text=answer))
    provider = ReportProvider(script)
    store = SessionStore(tmp_path / "sessions")
    manager = SessionManager(
        store,
        lambda: AgentRunner(config, provider=provider, runs_dir=tmp_path / "runs"),
        EventBus(),
    )
    session = await manager.create("chat")
    await manager.send_message(session.id, "Prepare a report")
    run_id = await manager.send_message(session.id, "Check tasks and assign a report code")
    assert manager.get_run_result(session.id, run_id).final_answer == answer
    assert sum(call["run_id"] == "compact" for call in provider.calls) == compactions
    messages = store.read_run_messages_strict(session.id, run_id)

    follow_up_run = await manager.send_message(session.id, follow_up)
    assert manager.get_run_result(session.id, follow_up_run).final_answer == "K-417"

    # Each real tool exchange is replayable exactly once, including across compactions.
    assert [m["role"] for m in messages] == ["assistant", "user"] * compactions + ["assistant"]
    assert [m["content"][0]["id"] for m in messages[:-1:2]] == tool_ids
    assert [m["content"][0]["tool_use_id"] for m in messages[1::2]] == tool_ids
