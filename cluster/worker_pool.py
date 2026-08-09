"""
Thread-safe WorkerPool managing active ClusterWorker nodes in the cluster.
"""

import threading
from uuid import UUID
from typing import Dict, List, Optional, Any

from cluster.worker import ClusterWorker
from cluster.models import WorkerState
from cluster.exceptions import WorkerNotFoundError, WorkerCapacityExceededError


class WorkerPool:
    """
    Thread-safe registry for worker node management, capacity tracking, and status querying.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._workers: Dict[UUID, ClusterWorker] = {}

    def register(self, worker: ClusterWorker) -> None:
        """Registers a worker node in the cluster pool."""
        with self._lock:
            self._workers[worker.node.worker_id] = worker

    def unregister(self, worker_id: UUID) -> None:
        """Unregisters a worker node from the cluster pool."""
        with self._lock:
            if worker_id in self._workers:
                self._workers[worker_id].shutdown()
                del self._workers[worker_id]

    def find_worker(self, worker_id: UUID) -> Optional[ClusterWorker]:
        """Retrieves a registered ClusterWorker by worker_id."""
        with self._lock:
            return self._workers.get(worker_id)

    def list_workers(self) -> List[ClusterWorker]:
        """Lists all registered ClusterWorker nodes."""
        with self._lock:
            return list(self._workers.values())

    def available_workers(self, provider: Optional[str] = None) -> List[ClusterWorker]:
        """
        Lists online workers with available capacity, optionally filtered by provider capability.
        """
        with self._lock:
            candidates: List[ClusterWorker] = []
            for w in self._workers.values():
                if w.node.status == WorkerState.ONLINE and w.node.current_load < w.node.maximum_capacity:
                    if provider is None or provider.lower() in [p.lower() for p in w.node.provider_capabilities]:
                        candidates.append(w)
            return candidates

    def capacity(self) -> Dict[str, int]:
        """Calculates total and current active capacity across the cluster pool."""
        with self._lock:
            total_cap = sum(w.node.maximum_capacity for w in self._workers.values())
            active_load = sum(w.node.current_load for w in self._workers.values())
            return {
                "total_capacity": total_cap,
                "active_load": active_load,
                "available_capacity": max(0, total_cap - active_load)
            }

    def statistics(self) -> Dict[str, Any]:
        """Computes summary statistics for the cluster worker pool."""
        with self._lock:
            cap = self.capacity()
            online_count = sum(1 for w in self._workers.values() if w.node.status == WorkerState.ONLINE)
            offline_count = sum(1 for w in self._workers.values() if w.node.status == WorkerState.OFFLINE)
            
            return {
                "total_workers": len(self._workers),
                "online_workers": online_count,
                "offline_workers": offline_count,
                "capacity": cap
            }
