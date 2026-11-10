import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("langgraph")

spec = importlib.util.spec_from_file_location(
    "operator_demo", Path(__file__).parents[2] / "examples/operator_workflow_demo.py"
)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def test_reject_wrong_output_and_order_regression():
    assert demo.decide(False, [10, 10], [8, 8]) == "reject"
    assert demo.decide(True, [10, 10], [8, 11]) == "reject"
    with pytest.raises(ValueError):
        demo.decide(True, [10, 10], [float("nan"), 8])


def run_to_review(graph, thread="test", attempts=3):
    config = {"configurable": {"thread_id": thread}}
    state = graph.invoke(demo.initial_state(attempts), config)
    return state, config


def test_pause_resume_does_not_repeat_evaluations():
    graph = demo.build_workflow()
    state, config = run_to_review(graph)
    assert state["__interrupt__"]
    assert graph.get_state(config).next == ("review",)
    assert state["accepted"] == "baseline"
    assert [r["decision"] for r in state["history"]] == ["reject", "keep"]
    result = graph.invoke(demo.Command(resume=True), config)
    assert result["accepted"] == "five-slab-rebalanced"
    assert result["review"] == "approved"
    assert result["history"] == state["history"]
    assert not graph.get_state(config).next


def test_review_rejection_retains_baseline():
    graph = demo.build_workflow()
    _, config = run_to_review(graph)
    result = graph.invoke(demo.Command(resume=False), config)
    assert result["accepted"] == "baseline"
    assert result["review"] == "rejected"


def test_attempt_budget_exits_before_second_candidate():
    state, _ = run_to_review(demo.build_workflow(), attempts=1)
    assert state["accepted"] == "baseline"
    assert len(state["history"]) == 1
    assert "__interrupt__" not in state


def test_incorrect_candidate_skips_benchmark(monkeypatch):
    monkeypatch.setattr(demo, "CANDIDATES", ({**demo.CANDIDATES[0], "correct": False},))
    state, _ = run_to_review(demo.build_workflow())
    assert state["accepted"] == "baseline"
    assert state["history"][0]["reason"] == "correctness_failed"
    assert "change_percent" not in state["history"][0]


def test_checkpoint_threads_are_isolated():
    graph = demo.build_workflow()
    _, first = run_to_review(graph, "first")
    _, second = run_to_review(graph, "second")
    graph.invoke(demo.Command(resume=False), first)
    assert graph.get_state(second).next == ("review",)
    assert graph.get_state(second).values["review"] == "pending"


def test_empty_candidates_and_invalid_budget(monkeypatch):
    monkeypatch.setattr(demo, "CANDIDATES", ())
    state, _ = run_to_review(demo.build_workflow())
    assert state["accepted"] == "baseline"
    assert state["history"] == []
    with pytest.raises(ValueError):
        demo.initial_state(0)
