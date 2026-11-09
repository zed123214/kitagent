"""Equal operator demo assets; measurements come from the executed harness."""

from __future__ import annotations

import json
import math

SPEC = """# Equal 算子开发任务

实现一维 Equal 算子 equal(a, b)，返回 bool 列表。
- 支持等长输入，以及长度为 1 的输入向另一侧广播。
- 两侧为空，或空输入与长度 1 的输入广播，返回空列表。
- 其他形状不兼容时抛出 ValueError；NaN 遵循 Python 比较语义。
- 优化思路：提前分派等长与广播路径，避免逐元素取模计算索引。
- 使用 check.py 对比独立基线；验证边界及固定种子的随机输入。
- 性能测试预热 3 次、采样 9 次并交替顺序，报告中位耗时。

计时包含输出列表分配。
模型决策由离线脚本固定；实现写入、验证和计时由真实工具执行。
"""

IMPLEMENTATION = '''"""One-dimensional Equal with scalar broadcasting."""


def equal(a, b):
    na, nb = len(a), len(b)
    if na == nb:
        return [x == y for x, y in zip(a, b)]
    if na == 1:
        scalar = a[0]
        return [scalar == y for y in b]
    if nb == 1:
        scalar = b[0]
        return [x == scalar for x in a]
    raise ValueError("incompatible shapes")
'''

CHECK_SCRIPT = '''"""Validate and benchmark the generated Equal implementation."""
import importlib.util
import json
import os
from pathlib import Path
import platform
import random
import statistics
import sys
import time


def reference(a, b):
    na, nb = len(a), len(b)
    if na != nb and na != 1 and nb != 1:
        raise ValueError("incompatible shapes")
    if na == 0 or nb == 0:
        return []
    return [a[i % na] == b[i % nb] for i in range(max(na, nb))]


def main():
    run_id, implementation = sys.argv[1:]
    time.sleep(float(os.environ.get("AGENTRT_DEMO_TOOL_DELAY", "0.5")))
    directory = Path("checks")
    directory.mkdir(exist_ok=True)
    # An approval refresh must never replay the benchmark command.
    with (directory / (run_id + ".txt")).open("x") as marker:
        marker.write("1")
    Path("check-count.txt").write_text(str(len(list(directory.iterdir()))))
    spec = importlib.util.spec_from_file_location("candidate", implementation)
    candidate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(candidate)
    cases = [
        ([1, 2, 3], [1, 0, 3], [True, False, True]),
        ([-1, 0, 2], [1, 0, -2], [False, True, False]),
        ([2], [1, 2, 2], [False, True, True]),
        ([1, 2, 2], [2], [False, True, True]),
        ([], [], []), ([], [1], []), ([1], [], []),
        ([float("nan"), float("inf"), -0.0],
         [float("nan"), float("inf"), 0.0], [False, True, True]),
    ]
    passed = 0
    for a, b, expected in cases:
        output = candidate.equal(a, b)
        assert output == expected and all(type(x) is bool for x in output)
        passed += 1
    for a, b in [([1, 2], [1, 2, 3]), ([], [1, 2]), ([1, 2], [])]:
        try:
            candidate.equal(a, b)
        except ValueError:
            passed += 1
        else:
            raise AssertionError("incompatible shapes must fail")
    rng = random.Random(42)
    for index in range(64):
        size = rng.randrange(2, 257)
        a = [rng.randrange(-4, 5) for _ in range(1 if index % 3 == 0 else size)]
        b = [rng.randrange(-4, 5) for _ in range(1 if index % 3 == 1 else size)]
        output = candidate.equal(a, b)
        assert output == reference(a, b) and all(type(x) is bool for x in output)
        passed += 1
    rows = []
    for size, broadcast in [(1024, False), (65536, False), (65536, True)]:
        a = [rng.randrange(8) for _ in range(size)]
        b = [3] if broadcast else [rng.randrange(8) for _ in range(size)]
        assert candidate.equal(a, b) == reference(a, b)
        for _ in range(3):
            reference(a, b)
            candidate.equal(a, b)
        samples = {"baseline": [], "candidate": []}
        functions = [("baseline", reference), ("candidate", candidate.equal)]
        for trial in range(9):
            for name, function in functions[::1 if trial % 2 == 0 else -1]:
                started = time.perf_counter_ns()
                function(a, b)
                samples[name].append((time.perf_counter_ns() - started) / 1_000_000)
        baseline = statistics.median(samples["baseline"])
        optimized = statistics.median(samples["candidate"])
        rows.append({"shape": f"{size} / {1 if broadcast else size}",
                     "baseline_ms": baseline, "optimized_ms": optimized,
                     "speedup": baseline / optimized, "samples_ms": samples})
    result = {"run_id": run_id, "passed": passed, "total": len(cases) + 3 + 64,
              "environment": (f"Python {platform.python_version()} / "
                              f"{platform.system()} {platform.machine()} / CPU"),
              "warmup": 3, "repeats": 9, "rows": rows}
    target = Path("benchmarks") / (run_id + ".json")
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"PASS: Equal correctness {passed}/{result['total']}")
    print("OPERATOR_RESULT=" + json.dumps(result))


if __name__ == "__main__":
    main()
'''


def measured_report(messages: list[dict[str, object]], run_id: str) -> str | None:
    """Only summarize a successful, matching tool result with measured samples."""
    for message in reversed(messages):
        content = message.get("content")
        if message.get("role") != "user" or not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_result":
                continue
            if block.get("is_error") or not isinstance(block.get("content"), str):
                continue
            for line in block["content"].splitlines():
                if not line.startswith("OPERATOR_RESULT="):
                    continue
                try:
                    result = json.loads(line.removeprefix("OPERATOR_RESULT="))
                    if result["run_id"] != run_id or result["passed"] != result["total"]:
                        continue
                    if result["total"] != 75 or len(result["rows"]) != 3:
                        continue
                    rows = []
                    for row in result["rows"]:
                        values = [row[key] for key in ("baseline_ms", "optimized_ms", "speedup")]
                        if not all(math.isfinite(value) and value > 0 for value in values):
                            raise ValueError("invalid measurements")
                        rows.append(
                            f"| {row['shape']} | {values[0]:.3f} | {values[1]:.3f} "
                            f"| {values[2]:.2f}× |"
                        )
                    return (
                        "## Equal 算子开发报告\n\n"
                        f"**正确性：{result['passed']}/{result['total']} 通过**"
                        "，覆盖等长输入、标量广播、空输入、特殊值与随机用例。\n\n"
                        "实现采用等长 / 广播路径分派，移除基线中的逐元素取模索引。\n\n"
                        "| 输入长度 A / B | 基线 ms | 优化 ms | 比值 |\n"
                        "| --- | ---: | ---: | ---: |\n" + "\n".join(rows) + "\n\n"
                        f"预热 {result['warmup']} 次，"
                        f"采样 {result['repeats']} 次，中位耗时，包含输出分配。\n\n"
                        f"实现：`operators/equal_{run_id}.py`\n\n"
                        f"原始计时：`benchmarks/{run_id}.json`\n\n"
                        f"运行标识：{run_id}\n"
                    )
                except (ValueError, KeyError, TypeError):
                    continue
    return None
