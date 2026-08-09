import pytest
from tests.test_execution_models import create_sample_execution_request
from cluster.worker import ClusterWorker
from cluster.models import WorkerState
from cluster.exceptions import WorkerError


def test_cluster_worker_lifecycle(monkeypatch):
    """Verify ClusterWorker start, heartbeat, execution, completion, and shutdown."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-123")

    worker = ClusterWorker()
    worker.start()
    assert worker.node.status == WorkerState.ONLINE

    hb = worker.heartbeat()
    assert hb.worker_id == worker.node.worker_id

    req = create_sample_execution_request()
    res = worker.execute_attack(req)

    assert res.status == "completed"
    assert res.provider == "openai"
    assert worker.node.current_load == 0

    worker.shutdown()
    assert worker.node.status == WorkerState.OFFLINE
