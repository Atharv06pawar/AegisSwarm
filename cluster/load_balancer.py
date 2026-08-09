"""
LoadBalancer module providing configurable load balancing algorithms across cluster workers.
"""

import threading
from typing import List, Optional

from cluster.worker import ClusterWorker
from cluster.models import WorkerState
from cluster.exceptions import WorkerCapacityExceededError


class LoadBalancer:
    """
    Load balancer selecting the optimal worker node for task execution based on configurable strategy.
    """

    def __init__(self, strategy: str = "least_loaded"):
        self.strategy = strategy.lower()
        self._lock = threading.RLock()
        self._rr_index = 0

    def select_worker(
        self,
        workers: List[ClusterWorker],
        provider: str,
        gpu_required: bool = False
    ) -> ClusterWorker:
        """
        Selects an available, non-overloaded worker matching provider and GPU constraints.
        """
        with self._lock:
            # Filter eligible candidates
            eligible = [
                w for w in workers
                if w.node.status == WorkerState.ONLINE
                and w.node.current_load < w.node.maximum_capacity
                and provider.lower() in [p.lower() for p in w.node.provider_capabilities]
            ]

            if gpu_required:
                eligible = [w for w in eligible if w.node.gpu_available]

            if not eligible:
                raise WorkerCapacityExceededError(f"No eligible worker available for provider '{provider}'.")

            if self.strategy == "round_robin":
                idx = self._rr_index % len(eligible)
                self._rr_index += 1
                return eligible[idx]

            elif self.strategy == "capability_aware":
                # Sort by number of supported capabilities matching provider
                eligible.sort(key=lambda w: (w.node.current_load, -len(w.node.provider_capabilities)))
                return eligible[0]

            elif self.strategy == "priority":
                # Sort by available capacity
                eligible.sort(key=lambda w: (w.node.maximum_capacity - w.node.current_load), reverse=True)
                return eligible[0]

            else:
                # Default: least_loaded
                eligible.sort(key=lambda w: w.node.current_load)
                return eligible[0]
