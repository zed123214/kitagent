from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from agent_runtime.cli.commands.run import _run_async
from agent_runtime.core.config import RuntimeConfig


@pytest.mark.parametrize(
    ("terminal_status", "expected_exit_code"),
    [(None, 1), ("success", 0), ("failed", 1)],
)
async def test_run_handles_daemon_eof(
    terminal_status: str | None, expected_exit_code: int, capsys: pytest.CaptureFixture[str]
) -> None:
    reader = asyncio.StreamReader()
    writer = Mock(spec=asyncio.StreamWriter)

    def send_response(data: bytes) -> None:
        request = json.loads(data)
        if request["method"] == "event.subscribe":
            result = {"sub_id": "sub-1"}
        else:
            assert request["method"] == "agent.run"
            result = {"run_id": "run-1"}
        messages = [{"jsonrpc": "2.0", "id": request["id"], "result": result}]

        if request["method"] == "agent.run" and terminal_status is not None:
            messages.extend(
                [
                    {"kind": "event", "event": {"type": "run.started", "run_id": "run-1"}},
                    {
                        "kind": "event",
                        "event": {
                            "type": "run.finished",
                            "run_id": "run-1",
                            "status": terminal_status,
                            "steps": 1,
                        },
                    },
                ]
            )

        reader.feed_data("".join(json.dumps(message) + "\n" for message in messages).encode())
        if request["method"] == "agent.run":
            reader.feed_eof()

    writer.write.side_effect = send_response
    with patch.object(asyncio, "open_connection", AsyncMock(return_value=(reader, writer))):
        exit_code = await asyncio.wait_for(_run_async("check the project", RuntimeConfig()), 1)

    assert exit_code == expected_exit_code
    writer.close.assert_called_once_with()
    captured = capsys.readouterr()
    if terminal_status is None:
        assert "core disconnected before run finished" in captured.err
    else:
        assert f"[run] {terminal_status}" in captured.out
        assert "core disconnected" not in captured.err
