"""Operator optimization state machine: routing, revision, review, and delivery."""

from __future__ import annotations

import argparse
import asyncio
import json
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
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
    phase: str
    review: str
    max_attempts: int


def initial_state(max_attempts: int = 3) -> State:
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")
    return State(
        index=0,
        history=[],
        accepted="baseline",
        decision="",
        phase="created",
        review="pending",
        max_attempts=max_attempts,
    )


def decide(correct: bool, baseline: list[float], candidate: list[float]) -> str:
    """Accept correct candidates that improve both paired execution orders."""
    import math

    if len(baseline) != 2 or len(candidate) != 2:
        raise ValueError("Exactly two execution orders are required")
    if any(not math.isfinite(v) or v <= 0 for v in baseline + candidate):
        raise ValueError("Timings must be finite and positive")
    return "keep" if correct and all(c < b for b, c in zip(baseline, candidate)) else "reject"


def build_workflow():
    def plan(state: State):
        return {"phase": "planned", "accepted": "baseline"}

    def validate(state: State):
        row = CANDIDATES[state["index"]]
        return {"phase": "validated", "decision": "valid" if row["correct"] else "incorrect"}

    def benchmark(state: State):
        row = CANDIDATES[state["index"]]
        decision = decide(row["correct"], row["baseline"], row["candidate"])
        changes = [(c / b - 1) * 100 for b, c in zip(row["baseline"], row["candidate"])]
        record = {**row, "change_percent": changes, "decision": decision}
        return {
            "history": [*state["history"], record],
            "decision": decision,
            "phase": "benchmarked",
        }

    def diagnose(state: State):
        history = state["history"]
        if state["decision"] == "incorrect":
            history = [
                *history,
                {
                    "name": CANDIDATES[state["index"]]["name"],
                    "decision": "reject",
                    "reason": "correctness_failed",
                },
            ]
        return {"index": state["index"] + 1, "history": history, "phase": "revising"}

    def review(state: State):
        answer = interrupt(
            {
                "candidate": CANDIDATES[state["index"]]["name"],
                "evidence": state["history"][-1],
                "question": "Approve this candidate for delivery?",
            }
        )
        if type(answer) is not bool:
            raise ValueError("Review decision must be a boolean")
        return {"review": "approved" if answer else "rejected", "phase": "reviewed"}

    def deliver(state: State):
        return {"accepted": CANDIDATES[state["index"]]["name"], "phase": "delivered"}

    def fallback(state: State):
        return {"accepted": "baseline", "phase": "baseline_retained"}

    def report(state: State):
        return {"phase": "completed"}

    def next_candidate(state: State):
        return (
            "validate"
            if state["index"] < min(len(CANDIDATES), state["max_attempts"])
            else "fallback"
        )

    graph = StateGraph(State)
    for name, node in [
        ("plan", plan),
        ("validate", validate),
        ("benchmark", benchmark),
        ("diagnose", diagnose),
        ("review", review),
        ("deliver", deliver),
        ("fallback", fallback),
        ("report", report),
    ]:
        graph.add_node(name, node)
    graph.add_edge(START, "plan")
    graph.add_conditional_edges("plan", next_candidate)
    graph.add_conditional_edges(
        "validate", lambda s: "benchmark" if s["decision"] == "valid" else "diagnose"
    )
    graph.add_conditional_edges(
        "benchmark", lambda s: "review" if s["decision"] == "keep" else "diagnose"
    )
    graph.add_conditional_edges("diagnose", next_candidate)
    graph.add_conditional_edges(
        "review", lambda s: "deliver" if s["review"] == "approved" else "fallback"
    )
    graph.add_edge("deliver", "report")
    graph.add_edge("fallback", "report")
    graph.add_edge("report", END)
    return graph.compile(checkpointer=InMemorySaver())


class OperatorWorkflowTool(BaseTool):
    name = "operator_workflow"
    description = "Evaluate operator candidates through a checkpointed approval workflow."
    input_schema = {"type": "object", "properties": {}, "additionalProperties": False}

    def __init__(self, review_policy: str = "approve", max_attempts: int = 3):
        self.review_policy = review_policy
        self.max_attempts = max_attempts
        self.report: dict[str, object] = {}

    async def invoke(self, params: dict[str, object]) -> ToolResult:
        graph = build_workflow()
        config = {"configurable": {"thread_id": "operator-iteration"}, "recursion_limit": 50}

        async def run(value):
            async for update in graph.astream(value, config=config, stream_mode="updates"):
                for node, delta in update.items():
                    if node != "__interrupt__":
                        print(f"workflow: {node:<10} {json.dumps(delta, ensure_ascii=False)}")

        await run(initial_state(self.max_attempts))
        snapshot = await graph.aget_state(config)
        if snapshot.next:
            print("checkpoint: review pending; previous evaluations saved")
            approved = self.review_policy == "approve"
            print(f"review policy: {self.review_policy}")
            await run(Command(resume=approved))
        self.report = dict((await graph.aget_state(config)).values)
        self.report["evidence_source"] = "archived operator experiments"
        print(f"selected={self.report['accepted']} review={self.report['review']}")
        return ToolResult(content=json.dumps(self.report, ensure_ascii=False))


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--review",
        choices=["approve", "reject"],
        default="approve",
        help="Decision used to resume the review checkpoint",
    )
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--output", help="Save the workflow state as a JSON report")
    args = parser.parse_args()
    initial_state(args.max_attempts)
    print("Operator Workflow | plan → validate → benchmark → review → deliver")
    workflow = OperatorWorkflowTool(args.review, args.max_attempts)
    registry = ToolRegistry()
    registry.register(workflow)
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
        "operator_workflow",
        {},
        final_text="Workflow finished. Review the selected version and decision history.",
    )
    try:
        result = await GraphExecutionEngine(provider, runtime=runtime).run(
            ExecutionContext(
                run_id="operator-demo",
                goal="Run the operator optimization state machine",
                max_steps=4,
            ),
            tools=registry,
            events=bus,
            config=EngineRunConfig(session_id="operator-demo", thread_id="operator-demo"),
        )
        print(f"runtime outcome={result.status}; {result.result}")
        if result.status != "success":
            raise RuntimeError(f"Demo failed: {result.status}")
        if not workflow.report:
            raise RuntimeError("Workflow tool did not produce a report")
        if args.output:
            from pathlib import Path

            Path(args.output).write_text(
                json.dumps(workflow.report, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"Report saved: {args.output}")
    finally:
        await runtime.close()


if __name__ == "__main__":
    asyncio.run(main())
