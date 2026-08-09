import pytest
from cluster.worker import ClusterWorker
from cluster.worker_pool import WorkerPool


def test_worker_pool_management():
    """Verify WorkerPool registration, query, available workers, capacity, and statistics."""
    pool = WorkerPool()
    w1 = ClusterWorker()
    w1.start()

    w2 = ClusterWorker()
    w2.start()

    pool.register(w1)
    pool.register(w2)

    assert len(pool.list_workers()) == 2
    assert pool.find_worker(w1.node.worker_id) == w1

    avail = pool.available_workers(provider="openai")
    assert len(avail) == 2

    cap = pool.capacity()
    assert cap["total_capacity"] == 20
    assert cap["active_load"] == 0

    stats = pool.statistics()
    assert stats["online_workers"] == 2

    pool.unregister(w1.node.worker_id)
    assert len(pool.list_workers()) == 1
