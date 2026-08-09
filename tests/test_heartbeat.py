import pytest
from cluster.worker import ClusterWorker
from cluster.worker_pool import WorkerPool
from cluster.heartbeat import HeartbeatMonitor
from cluster.models import WorkerState


def test_heartbeat_monitor():
    """Verify HeartbeatMonitor records payload heartbeats and identifies healthy vs dead workers."""
    pool = WorkerPool()
    worker = ClusterWorker()
    worker.start()
    pool.register(worker)

    monitor = HeartbeatMonitor(pool=pool)
    payload = worker.heartbeat()
    monitor.record_heartbeat(payload)

    health = monitor.check_health()
    assert str(worker.node.worker_id) in health["healthy"]
    assert len(health["dead"]) == 0
