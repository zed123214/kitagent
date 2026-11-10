"""Offline historical-evidence replay; no model API, compilation, or NPU execution."""

from __future__ import annotations

import asyncio
import json
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from agent_runtime.core.context import ExecutionContext
from agent_runtime.core.engine.base import EngineRunConfig
from agent_runtime.core.events.bus import EventBus
from agent_runtime.core.graph.engine import GraphExecutionEngine
from agent_runtime.core.graph.fake_provider import ScriptedProvider
from agent_runtime.core.graph.runtime import GraphRuntime
from agent_runtime.core.tools.base import BaseTool, ToolResult
from agent_runtime.core.tools.registry import ToolRegistry

# Historical records, not measurements made by this demo. Each experiment has
# its OWN paired control. Never subtract timings across experiments.
CANDIDATES = (
    {
        "name": "five-slab-initial",
        "baseline": [277.131073, 281.79126],
        "candidate": [290.331604, 285.931427],
        "correct": True,
        "source": "five-slab initial stage record",
    },
    {
        "name": "five-slab-rebalanced",
        "baseline": [280.171204, 275.311005],
        "candidate": [258.990356, 259.710388],
        "correct": True,
        "source": "E11/DECISION.json",
    },
)


class State(TypedDict):
    index: int
    history: list[dict[str, object]]
    accepted: str
    decision: str


def decide(correct: bool, baseline: list[float], candidate: list[float]) -> str:
    """A conservative DEMO gate, not an official competition scoring rule."""
    import math

    if len(baseline) != 2 or len(candidate) != 2:
        raise ValueError("Exactly two execution orders are required")
    if any(not math.isfinite(v) or v <= 0 for v in baseline + candidate):
        raise ValueError("Timings must be finite and positive")
    return "keep" if correct and all(c < b for b, c in zip(baseline, candidate)) else "reject"


def build_workflow():
    def contract(state: State):
        print("contract: Equal broadcast/BOOL; SFAG repeated indices and all present gradients")
        print("matrix: dtype x mode x RoPE x Value x tails; untested cells remain pending")
        return {"accepted": "baseline"}

    def evaluate(state: State):
        row = CANDIDATES[state["index"]]
        decision = decide(row["correct"], row["baseline"], row["candidate"])
        changes = [(c / b - 1) * 100 for b, c in zip(row["baseline"], row["candidate"])]
        record = {**row, "change_percent": changes, "decision": decision}
        print(f"evaluate: {row['name']} {decision} {changes[0]:+.2f}% / {changes[1]:+.2f}%")
        return {"history": [*state["history"], record], "decision": decision}

    def reject(state: State):
        print("reject: retain baseline; diagnose short-slab dK/dV tail; revise ownership")
        return {"index": state["index"] + 1}

    def keep(state: State):
        return {"accepted": CANDIDATES[state["index"]]["name"]}

    def report(state: State):
        print(f"report: selected={state['accepted']}; device rerun=PENDING")
        return {}

    graph = StateGraph(State)
    for name, node in [
        ("contract", contract),
        ("evaluate", evaluate),
        ("reject", reject),
        ("keep", keep),
        ("report", report),
    ]:
        graph.add_node(name, node)
    graph.add_edge(START, "contract")
    graph.add_edge("contract", "evaluate")
    graph.add_conditional_edges(
        "evaluate", lambda s: s["decision"], {"keep": "keep", "reject": "reject"}
    )
    graph.add_conditional_edges(
        "reject", lambda s: "evaluate" if s["index"] < len(CANDIDATES) else "report"
    )
    graph.add_edge("keep", "report")
    graph.add_edge("report", END)
    return graph.compile()


class ReplayTool(BaseTool):
    name = "operator_evidence_replay"
    description = "Run a local LangGraph over archived operator evidence; no device execution."
    input_schema = {"type": "object", "properties": {}, "additionalProperties": False}

    async def invoke(self, params: dict[str, object]) -> ToolResult:
        state = await build_workflow().ainvoke(
            {"index": 0, "history": [], "accepted": "baseline", "decision": ""},
            config={"recursion_limit": 20},
        )
        return ToolResult(content=json.dumps({"mode": "historical-replay", **state}))


async def main() -> None:
    print("OFFLINE REPLAY | scripted provider | archived evidence | NO NPU measurements")
    registry = ToolRegistry()
    registry.register(ReplayTool())
    bus = EventBus(correlation_id="operator-demo", session_id="operator-demo")

    async def show(event: BaseModel) -> None:
        data = event.model_dump()
        if data.get("type") in {"node.started", "node.finished", "state.diff"}:
            print(f"runtime: {data.get('type')} node={data.get('node_id')}")
        if data.get("type") == "tool.finished":
            print(json.dumps(data, ensure_ascii=False, default=str))

    bus.subscribe(show)
    runtime = GraphRuntime()
    provider = ScriptedProvider.tool(
        "operator_evidence_replay",
        {},
        final_text="Evidence replay complete. Device validation remains pending.",
    )
    try:
        result = await GraphExecutionEngine(provider, runtime=runtime).run(
            ExecutionContext(
                run_id="operator-demo", goal="Replay operator optimization decisions", max_steps=4
            ),
            tools=registry,
            events=bus,
            config=EngineRunConfig(session_id="operator-demo", thread_id="operator-demo"),
        )
        print(f"runtime outcome={result.status}; {result.result}")
        if result.status != "success":
            raise RuntimeError(f"Demo failed: {result.status}")
    finally:
        await runtime.close()


if __name__ == "__main__":
    asyncio.run(main())
