"""
Unit tests for OrchestratorDispatcher in orchestrator package.
"""

from orchestrator.dispatcher import OrchestratorDispatcher


def test_dispatcher_batch():
    dispatcher = OrchestratorDispatcher()
    tasks = [
        {"task_id": "t-1", "estimated_cost": 0.002},
        {"task_id": "t-2", "estimated_cost": 0.002}
    ]
    res = dispatcher.dispatch_batch(tasks)

    assert res["total_dispatched"] == 2
    assert res["successful_count"] == 2
    assert res["failed_count"] == 0
    assert len(res["results"]) == 2
