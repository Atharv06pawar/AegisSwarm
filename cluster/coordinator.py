"""
ClusterCoordinator module managing cluster lifecycles, health checks, and metadata.
"""

import logging
from typing import Optional, Dict, Any

from cluster.worker_pool import WorkerPool
from cluster.worker_manager import WorkerManager
from cluster.heartbeat import HeartbeatMonitor
from cluster.scheduler import DistributedScheduler
from cluster.persistence import ClusterPersistence
from cluster.models import ClusterStateModel
from observability.event_bus import EventBus
from observability.events import create_telemetry_event

logger = logging.getLogger(__name__)


class ClusterCoordinator:
    """
    Coordinator control plane orchestrating cluster startup, worker registration, health checks, and metadata.
    """

    def __init__(
        self,
        worker_manager: Optional[WorkerManager] = None,
        scheduler: Optional[DistributedScheduler] = None,
        heartbeat_monitor: Optional[HeartbeatMonitor] = None,
        persistence: Optional[ClusterPersistence] = None,
        event_bus: Optional[EventBus] = None
    ):
        self.worker_manager = worker_manager or WorkerManager()
        self.pool = self.worker_manager.pool
        self.scheduler = scheduler or DistributedScheduler()
        self.heartbeat_monitor = heartbeat_monitor or HeartbeatMonitor(pool=self.pool)
        self.persistence = persistence or ClusterPersistence()
        self.event_bus = event_bus or EventBus()
        self.leader_id: str = "node-leader-main"

    def start_cluster(self, initial_workers: int = 2) -> ClusterStateModel:
        """Starts cluster control plane and initializes default worker pool."""
        self.worker_manager.scale_cluster(initial_workers)
        
        self.event_bus.publish(
            create_telemetry_event(
                component="coordinator",
                event_type="ClusterStarted",
                payload={"initial_workers": initial_workers, "leader": self.leader_id}
            )
        )
        return self.get_cluster_state()

    def get_cluster_state(self) -> ClusterStateModel:
        """Assembles current ClusterStateModel snapshot."""
        stats = self.pool.statistics()
        state = ClusterStateModel(
            total_workers=stats["total_workers"],
            online_workers=stats["online_workers"],
            total_capacity=stats["capacity"]["total_capacity"],
            active_executions=stats["capacity"]["active_load"],
            queued_tasks=self.scheduler.queue_size()
        )
        self.persistence.save_cluster_state(state)
        return state

    def check_health(self) -> Dict[str, Any]:
        """Runs heartbeat health scan across registered workers."""
        health = self.heartbeat_monitor.check_health()
        state = self.get_cluster_state()
        return {
            "cluster_state": state.model_dump(),
            "worker_health": health
        }
