import pytest
from cluster.models import WorkerNode, WorkerState, ClusterTask, HeartbeatPayload, ClusterStateModel


def test_worker_node_model():
    """Verify WorkerNode model default initialization and fields."""
    node = WorkerNode(hostname="test-node", cpu_cores=8, memory_gb=16.0)
    assert node.hostname == "test-node"
    assert node.status == WorkerState.ONLINE
    assert "openai" in node.provider_capabilities


def test_cluster_task_model():
    """Verify ClusterTask model initialization."""
    task = ClusterTask(attack_record_id="rec-1", provider="openai", model="gpt-4o", priority=5)
    assert task.attack_record_id == "rec-1"
    assert task.status == "QUEUED"
    assert task.priority == 5


def test_heartbeat_payload_model():
    """Verify HeartbeatPayload model instantiation."""
    node = WorkerNode()
    hb = HeartbeatPayload(worker_id=node.worker_id, cpu_usage_pct=25.0)
    assert hb.worker_id == node.worker_id
    assert hb.cpu_usage_pct == 25.0
