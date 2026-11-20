from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any, cast

from openai import AsyncOpenAI, omit
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

from agent_runtime.core.bus.events import LlmModelSelectedEvent, LlmTokenEvent, LlmUsageEvent
from agent_runtime.core.events.bus import EventBus
from agent_runtime.core.llm.base import DEFAULT_SYSTEM_PROMPT
from agent_runtime.core.llm.types import LlmResponse, ToolCallBlock, UsageStats


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _messages(history: list[dict[str, object]], system: str) -> list[ChatCompletionMessageParam]:
    messages: list[dict[str, Any]] = [{"role": "system", "content": system}]
    for message in history:
        role, content = message["role"], message["content"]
        if isinstance(content, str):
            messages.append({"role": role, "content": content})
            continue
        if not isinstance(content, list):
            raise ValueError("Unsupported message content")
        text = []
        calls = []
        for block in content:
            match block["type"]:
                case "text":
                    text.append(block["text"])
                case "tool_use":
                    calls.append(
                        {
                            "type": "function",
                            "id": block["id"],
                            "function": {
                                "name": block["name"],
                                "arguments": json.dumps(block["input"], ensure_ascii=False),
                            },
                        }
                    )
                case "tool_result":
                    result = block["content"]
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": block["tool_use_id"],
                            "content": f"Error: {result}" if block.get("is_error") else result,
                        }
                    )
                case "thinking" | "redacted_thinking":
                    continue  # Anthropic-only blocks in saved conversations.
                case _:
                    raise ValueError(f"Unsupported message block: {block['type']}")
        if text or calls:
            item: dict[str, Any] = {"role": role, "content": "".join(text) or None}
            if calls:
                item["tool_calls"] = calls
            messages.append(item)
    return cast(list[ChatCompletionMessageParam], messages)


@dataclass
class _PendingCall:
    id: str = ""
    name: str = ""
    arguments: str = ""

    def finish(self, truncated: bool) -> ToolCallBlock:
        if not self.id or not self.name:
            raise ValueError("OpenAI returned a function call without an ID or name")
        # The engines synthesize an error result for truncated calls and never invoke them.
        arguments = {} if truncated else json.loads(self.arguments)
        if not isinstance(arguments, dict):
            raise ValueError("OpenAI function arguments must be a JSON object")
        return ToolCallBlock(self.id, self.name, arguments)


class OpenAIProvider:
    def __init__(self, model: str) -> None:
        self._model = model
        self._api_key = os.environ.get("OPENAI_API_KEY")
        if not self._api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self._base_url = os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1"

    async def chat(
        self,
        messages: list[dict[str, object]],
        tool_schemas: list[dict[str, object]],
        bus: EventBus,
        run_id: str,
        *,
        step: int = 0,
        system: str | None = None,
    ) -> LlmResponse:
        await bus.publish(
            LlmModelSelectedEvent(run_id=run_id, model=self._model, strategy="static", ts=_now())
        )
        tools = cast(
            list[ChatCompletionToolParam],
            [
                {
                    "type": "function",
                    "function": {
                        "name": schema["name"],
                        "description": schema.get("description", ""),
                        "parameters": schema["input_schema"],
                    },
                }
                for schema in tool_schemas
            ],
        )
        text: list[str] = []
        calls: dict[int, _PendingCall] = {}
        finish_reason = None
        usage = None
        async with AsyncOpenAI(api_key=self._api_key, base_url=self._base_url) as client:
            stream = await client.chat.completions.create(
                model=self._model,
                messages=_messages(messages, system or DEFAULT_SYSTEM_PROMPT),
                tools=tools or omit,
                stream=True,
                stream_options={"include_usage": True},
                max_completion_tokens=8192,
            )
            async for chunk in stream:
                if chunk.usage:
                    usage = chunk.usage
                for choice in chunk.choices:
                    token = choice.delta.content or choice.delta.refusal
                    if token:
                        text.append(token)
                        await bus.publish(LlmTokenEvent(run_id=run_id, token=token, ts=_now()))
                    for fragment in choice.delta.tool_calls or []:
                        call = calls.setdefault(fragment.index, _PendingCall())
                        if fragment.id:
                            call.id = fragment.id
                        if fragment.function:
                            call.name += fragment.function.name or ""
                            call.arguments += fragment.function.arguments or ""
                    if choice.finish_reason:
                        finish_reason = choice.finish_reason

        reasons = {"stop": "end_turn", "tool_calls": "tool_use", "length": "max_tokens"}
        if finish_reason not in reasons:
            raise ValueError(f"OpenAI stream ended with finish_reason={finish_reason!r}")
        if (finish_reason == "tool_calls" and not calls) or (finish_reason == "stop" and calls):
            raise ValueError("OpenAI finish reason conflicts with the returned tool calls")
        response = LlmResponse(
            stop_reason=reasons[finish_reason],
            text="".join(text),
            tool_calls=[calls[i].finish(finish_reason == "length") for i in sorted(calls)],
        )
        if usage:
            details = usage.prompt_tokens_details
            cached = (details.cached_tokens or 0) if details else 0
            # Alias deployments may not expose their underlying model's context window.
            window = 1_047_576 if self._model.startswith("gpt-4.1") else 128_000
            response.usage = UsageStats(
                input_tokens=usage.prompt_tokens - cached,
                output_tokens=usage.completion_tokens,
                cache_read_input_tokens=cached,
                context_pct=usage.prompt_tokens / window,
            )
            await bus.publish(LlmUsageEvent(run_id=run_id, ts=_now(), **asdict(response.usage)))
        return response
