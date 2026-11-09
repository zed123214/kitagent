from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from agent_runtime.web.demo_operator import CHECK_SCRIPT, IMPLEMENTATION, measured_report


def run_check(directory: Path, implementation: str = IMPLEMENTATION):
    (directory / "equal.py").write_text(implementation, encoding="utf-8")
    (directory / "check.py").write_text(CHECK_SCRIPT, encoding="utf-8")
    return subprocess.run(
        [sys.executable, "check.py", "test-run", "equal.py"],
        cwd=directory,
        env={**os.environ, "AGENTRT_DEMO_TOOL_DELAY": "0"},
        capture_output=True,
        text=True,
        timeout=20,
    )


def tool_messages(output: str, *, is_error: bool = False):
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "validate-benchmark",
                    "content": output,
                    "is_error": is_error,
                }
            ],
        }
    ]


def test_equal_demo_validates_benchmarks_and_rejects_replay(tmp_path: Path):
    result = run_check(tmp_path)
    assert result.returncode == 0, result.stderr
    assert "PASS: Equal correctness 75/75" in result.stdout
    evidence = json.loads((tmp_path / "benchmarks/test-run.json").read_text())
    assert evidence["passed"] == evidence["total"] == 75
    for row in evidence["rows"]:
        assert len(row["samples_ms"]["candidate"]) == 9
        assert len(row["samples_ms"]["baseline"]) == 9
        assert row["speedup"] == pytest.approx(row["baseline_ms"] / row["optimized_ms"])
    report = measured_report(tool_messages(result.stdout), "test-run")
    assert report and "75/75" in report and "基线 ms" in report
    assert "预热 3 次，采样 9 次" in report
    assert measured_report(tool_messages(result.stdout), "different-run") is None
    assert measured_report(tool_messages(result.stdout, is_error=True), "test-run") is None
    replay = run_check(tmp_path)
    assert replay.returncode != 0
    assert "FileExistsError" in replay.stderr
    assert (tmp_path / "check-count.txt").read_text() == "1"


def test_equal_demo_rejects_incorrect_operator(tmp_path: Path):
    result = run_check(tmp_path, "def equal(a, b): return [True] * len(a)\n")
    assert result.returncode != 0
    assert "OPERATOR_RESULT=" not in result.stdout
    assert not (tmp_path / "benchmarks/test-run.json").exists()
    assert measured_report(tool_messages(result.stdout), "test-run") is None


@pytest.mark.parametrize(
    "payload", ["not json", "{}", '{"run_id": "test-run", "passed": 0, "total": 75}']
)
def test_missing_or_failed_measurements_do_not_produce_report(payload: str):
    assert measured_report(tool_messages("OPERATOR_RESULT=" + payload), "test-run") is None
