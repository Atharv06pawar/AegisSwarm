import pytest
from cluster.worker import ClusterWorker
from cluster.models import WorkerNode
from cluster.load_balancer import LoadBalancer
from cluster.exceptions import WorkerCapacityExceededError


def test_load_balancer_strategies():
    """Verify LoadBalancer worker selection across least_loaded, round_robin, capability_aware, priority."""
    w1 = ClusterWorker(node=WorkerNode(hostname="n1", current_load=2))
    w1.start()
    w2 = ClusterWorker(node=WorkerNode(hostname="n2", current_load=0))
    w2.start()

    workers = [w1, w2]

    lb_least = LoadBalancer(strategy="least_loaded")
    selected_least = lb_least.select_worker(workers, provider="openai")
    assert selected_least == w2

    lb_rr = LoadBalancer(strategy="round_robin")
    sel1 = lb_rr.select_worker(workers, provider="openai")
    sel2 = lb_rr.select_worker(workers, provider="openai")
    assert sel1 != sel2

    lb_cap = LoadBalancer(strategy="capability_aware")
    sel_cap = lb_cap.select_worker(workers, provider="openai")
    assert sel_cap in workers

    lb_prio = LoadBalancer(strategy="priority")
    sel_prio = lb_prio.select_worker(workers, provider="openai")
    assert sel_prio == w2


def test_load_balancer_no_eligible_workers():
    """Verify LoadBalancer raises WorkerCapacityExceededError when no workers match constraints."""
    lb = LoadBalancer()
    with pytest.raises(WorkerCapacityExceededError):
        lb.select_worker([], provider="openai")
