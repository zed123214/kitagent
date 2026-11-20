from __future__ import annotations

from typing import Protocol

from agent_runtime.core.events.bus import EventBus
from agent_runtime.core.llm.types import LlmResponse

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful AI assistant. "
    "Use the available tools to complete the user's goal. "
    "When the goal is fully achieved, respond with a final answer and do not call any more tools."
)


class LLMProvider(Protocol):
    # 流式调用 LLM 并发布进度事件，返回完整响应
    async def chat(
        self,
        messages: list[dict[str, object]],
        tool_schemas: list[dict[str, object]],
        bus: EventBus,
        run_id: str,
        *,
        step: int = 0,
        system: str | None = None,
    ) -> LlmResponse: ...
