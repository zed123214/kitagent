from __future__ import annotations

import asyncio
import json
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from agent_runtime.core.transport.socket_client import IpcError, SocketClient


@pytest.fixture
def client_with_writer() -> tuple[SocketClient, Mock]:
    client = SocketClient("127.0.0.1", 0)
    writer = Mock(spec=asyncio.StreamWriter)
    writer.drain = AsyncMock()
    client._writer = writer
    return client, writer


@pytest.mark.parametrize("stage", ["write", "drain"])
async def test_failed_send_removes_pending_request(
    client_with_writer: tuple[SocketClient, Mock], stage: str
) -> None:
    client, writer = client_with_writer
    getattr(writer, stage).side_effect = OSError("send failed")

    with pytest.raises(OSError, match="send failed"):
        await client.send_command("core.ping", {})

    assert client._pending == {}


async def test_serialization_failure_removes_pending_request(
    client_with_writer: tuple[SocketClient, Mock],
) -> None:
    client, writer = client_with_writer

    with pytest.raises(ValueError):
        await client.send_command("core.ping", {"unsupported": object()})

    writer.write.assert_not_called()
    assert client._pending == {}


@pytest.mark.parametrize("stage", ["drain", "response"])
async def test_cancelled_send_cleans_up_without_affecting_other_requests(
    client_with_writer: tuple[SocketClient, Mock], stage: str
) -> None:
    client, writer = client_with_writer
    first_started = asyncio.Event()
    second_started = asyncio.Event()
    release_drain = asyncio.Event()

    async def drain() -> None:
        if not first_started.is_set():
            first_started.set()
            if stage == "drain":
                await release_drain.wait()
        else:
            second_started.set()

    writer.drain.side_effect = drain
    first = asyncio.create_task(client.send_command("core.ping", {}))
    second: asyncio.Task[dict[str, Any]] | None = None
    try:
        await asyncio.wait_for(first_started.wait(), timeout=2.0)
        first_id = json.loads(writer.write.call_args.args[0])["id"]
        first_future = client._pending[first_id]
        second = asyncio.create_task(client.send_command("core.ping", {}))
        await asyncio.wait_for(second_started.wait(), timeout=2.0)
        second_id = json.loads(writer.write.call_args.args[0])["id"]

        first.cancel()
        with pytest.raises(asyncio.CancelledError):
            await first

        assert first_id not in client._pending
        assert first_future.cancelled()
        assert set(client._pending) == {second_id}
        await client._dispatch(
            json.dumps({"jsonrpc": "2.0", "id": first_id, "result": {"late": True}}).encode()
        )
        assert not second.done()
        await client._dispatch(
            json.dumps({"jsonrpc": "2.0", "id": second_id, "result": {"pong": True}}).encode()
        )
        assert await asyncio.wait_for(second, timeout=2.0) == {"pong": True}
        assert client._pending == {}
    finally:
        tasks = [first] if second is None else [first, second]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


async def _start_mock_server(
    handler: Any,
) -> tuple[asyncio.Server, int]:
    server = await asyncio.start_server(handler, "127.0.0.1", 0)
    port: int = server.sockets[0].getsockname()[1]
    return server, port


# 功能：验证 send_command 向 mock server 发送 JSON-RPC 请求并正确解析响应 result
# 设计：用 asyncio.start_server + port 0 启动内存中的 mock server，避免依赖真实 daemon；
#       loop_task 并发运行 run_event_loop，使 send_command 的 future 能被 _dispatch 解析
async def test_send_command_returns_result() -> None:
    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        line = await reader.readline()
        req = json.loads(line)
        resp = {"jsonrpc": "2.0", "id": req["id"], "result": {"pong": True}}
        writer.write(json.dumps(resp).encode() + b"\n")
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    server, port = await _start_mock_server(handle)
    async with server:
        client = SocketClient("127.0.0.1", port)
        await client.connect()
        loop_task = asyncio.create_task(client.run_event_loop())

        result = await asyncio.wait_for(
            client.send_command("core.ping", {"client": "test"}),
            timeout=2.0,
        )
        assert result == {"pong": True}

        await loop_task
        await client.close()


# 功能：验证 server 返回 JSON-RPC error 时 send_command 抛出 IpcError 并携带正确错误码
# 设计：mock server 返回 error 对象（code=-32601），断言异常类型和 code 属性，确认客户端的错误路径处理
async def test_send_command_raises_ipc_error() -> None:
    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        line = await reader.readline()
        req = json.loads(line)
        resp = {
            "jsonrpc": "2.0",
            "id": req["id"],
            "error": {"code": -32601, "message": "Method not found"},
        }
        writer.write(json.dumps(resp).encode() + b"\n")
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    server, port = await _start_mock_server(handle)
    async with server:
        client = SocketClient("127.0.0.1", port)
        await client.connect()
        loop_task = asyncio.create_task(client.run_event_loop())

        with pytest.raises(IpcError) as exc_info:
            await asyncio.wait_for(
                client.send_command("core.nope", {}),
                timeout=2.0,
            )
        assert exc_info.value.code == -32601

        await loop_task
        await client.close()


# 功能：验证 server 推送 kind=event 的消息时，on_event 注册的 handler 能收到 event 字典
# 设计：server 先返回 RPC 响应（解除 send_command 的等待），再推送事件；用 asyncio.Event 等待 handler 被调用，
#       避免 sleep 轮询；断言 event 内容中的 type 字段是否正确
async def test_event_push_routed_to_handler() -> None:
    received_events: list[dict[str, Any]] = []
    push_done = asyncio.Event()

    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        line = await reader.readline()
        req = json.loads(line)
        resp = {"jsonrpc": "2.0", "id": req["id"], "result": {"subscription_id": "sub-1"}}
        writer.write(json.dumps(resp).encode() + b"\n")
        push = {"kind": "event", "event": {"type": "run.started", "run_id": "r1"}}
        writer.write(json.dumps(push).encode() + b"\n")
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    server, port = await _start_mock_server(handle)
    async with server:
        client = SocketClient("127.0.0.1", port)

        async def collect(event_data: dict[str, Any]) -> None:
            received_events.append(event_data)
            push_done.set()

        client.on_event(collect)
        await client.connect()
        loop_task = asyncio.create_task(client.run_event_loop())

        await asyncio.wait_for(
            client.send_command("event.subscribe", {"topics": ["run.*"]}),
            timeout=2.0,
        )
        await asyncio.wait_for(push_done.wait(), timeout=2.0)

        assert len(received_events) == 1
        assert received_events[0]["type"] == "run.started"

        await loop_task
        await client.close()


# 功能：验证 server 关闭连接后 run_event_loop 正常退出（不挂起）
# 设计：mock server 立即关闭写流，client readline 收到空字节后退出循环；
#       用 asyncio.wait_for 设置超时，防止 loop 意外挂起导致测试卡死
async def test_run_event_loop_exits_on_server_close() -> None:
    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        writer.close()
        await writer.wait_closed()

    server, port = await _start_mock_server(handle)
    async with server:
        client = SocketClient("127.0.0.1", port)
        await client.connect()
        await asyncio.wait_for(client.run_event_loop(), timeout=2.0)
        await client.close()
