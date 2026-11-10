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


def test_real_graph_rejects_then_promotes():
    state = demo.build_workflow().invoke(
        {"index": 0, "history": [], "accepted": "", "decision": ""}
    )
    assert [row["decision"] for row in state["history"]] == ["reject", "keep"]
    assert state["accepted"] == "five-slab-rebalanced"


def test_all_rejected_retains_baseline(monkeypatch):
    monkeypatch.setattr(demo, "CANDIDATES", (demo.CANDIDATES[0],))
    state = demo.build_workflow().invoke(
        {"index": 0, "history": [], "accepted": "", "decision": ""}
    )
    assert state["accepted"] == "baseline"
    assert len(state["history"]) == 1
