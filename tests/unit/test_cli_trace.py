from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent_runtime.cli.commands import trace
from agent_runtime.core.config import RuntimeConfig
from agent_runtime.core.trace.record import TraceRecord


def test_trace_follow_keeps_records_appended_after_backlog(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "trace.jsonl"
    config = RuntimeConfig()
    config.trace.file = str(path)
    record = TraceRecord(
        ts="2026-11-12T00:00:00Z", direction="CORE", layer="event", kind="event", data={}
    )
    backlog = record.model_copy(update={"run_id": "backlog"}).model_dump_json()
    appended = record.model_copy(update={"run_id": "appended"}).model_dump_json()
    path.write_text(backlog + "\n", encoding="utf-8")

    with path.open(encoding="utf-8") as original, path.open(encoding="utf-8") as reopened:

        def read_backlog() -> Iterator[str]:
            yield from original
            with path.open("a", encoding="utf-8") as writer:
                writer.write(appended + "\n")

        stream = MagicMock(wraps=original)
        stream.__enter__.return_value = stream
        stream.__iter__.side_effect = read_backlog
        with (
            patch.object(trace, "open", side_effect=[stream, reopened], create=True),
            patch.object(trace.time, "sleep", side_effect=KeyboardInterrupt),
            pytest.raises(KeyboardInterrupt),
        ):
            trace.cmd_trace(None, config, raw=True, follow=True)

    assert capsys.readouterr().out.splitlines() == [backlog, appended]
