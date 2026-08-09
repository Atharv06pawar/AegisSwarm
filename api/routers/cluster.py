"""
FastAPI Router for Distributed Worker Cluster management endpoints.
"""

from uuid import UUID
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException

from cluster.models import WorkerNode, ClusterStateModel
from cluster.coordinator import ClusterCoordinator
from api.dependencies import get_cluster_coordinator

cluster_router = APIRouter(prefix="/cluster", tags=["Distributed Cluster Subsystem"])


@cluster_router.get("", response_model=ClusterStateModel)
def get_cluster_overview(
    coordinator: ClusterCoordinator = Depends(get_cluster_coordinator)
):
    """Retrieves cluster state snapshot metadata."""
    return coordinator.get_cluster_state()


@cluster_router.get("/workers", response_model=List[WorkerNode])
def list_cluster_workers(
    coordinator: ClusterCoordinator = Depends(get_cluster_coordinator)
):
    """Lists all registered cluster worker nodes."""
    return [w.node for w in coordinator.pool.list_workers()]


@cluster_router.get("/workers/{worker_id}", response_model=WorkerNode)
def get_cluster_worker(
    worker_id: UUID,
    coordinator: ClusterCoordinator = Depends(get_cluster_coordinator)
):
    """Retrieves a specific cluster worker by UUID."""
    worker = coordinator.pool.find_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail=f"Worker '{worker_id}' not found.")
    return worker.node


@cluster_router.get("/health")
def get_cluster_health(
    coordinator: ClusterCoordinator = Depends(get_cluster_coordinator)
):
    """Scans and returns worker node heartbeat health status."""
    return coordinator.check_health()


@cluster_router.get("/statistics")
def get_cluster_statistics(
    coordinator: ClusterCoordinator = Depends(get_cluster_coordinator)
):
    """Retrieves cluster worker pool statistics and capacity metrics."""
    return coordinator.pool.statistics()


@cluster_router.post("/register", response_model=WorkerNode, status_code=201)
def register_cluster_worker(
    hostname: str = "node-custom",
    capabilities: Optional[List[str]] = None,
    coordinator: ClusterCoordinator = Depends(get_cluster_coordinator)
):
    """Registers a new worker node in the cluster."""
    worker = coordinator.worker_manager.add_worker(hostname=hostname, capabilities=capabilities)
    return worker.node


@cluster_router.post("/shutdown")
def shutdown_cluster_worker(
    worker_id: UUID,
    coordinator: ClusterCoordinator = Depends(get_cluster_coordinator)
):
    """Shuts down and unregisters a specified worker node."""
    worker = coordinator.pool.find_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail=f"Worker '{worker_id}' not found.")
    coordinator.worker_manager.remove_worker(worker_id)
    return {"status": "shutdown_completed", "worker_id": str(worker_id)}


@cluster_router.post("/rebalance")
def rebalance_cluster_workers(
    target_count: int = 4,
    coordinator: ClusterCoordinator = Depends(get_cluster_coordinator)
):
    """Rebalances and scales cluster worker nodes to match target count."""
    workers = coordinator.worker_manager.scale_cluster(target_count)
    return {"status": "rebalanced", "target_count": target_count, "active_workers": len(workers)}
