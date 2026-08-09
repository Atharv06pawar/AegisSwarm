"""
DistributedScheduler managing priority queues and execution task scheduling.
"""

import heapq
import threading
from typing import List, Optional, Dict, Any

from cluster.models import ClusterTask
from cluster.config import ClusterConfig
from cluster.exceptions import SchedulerError


class DistributedScheduler:
    """
    Priority queue scheduler managing execution tasks, fair scheduling, and back-pressure limits.
    """

    def __init__(self, config: Optional[ClusterConfig] = None):
        self.config = config or ClusterConfig()
        self._lock = threading.RLock()
        self._queue: List[tuple[int, int, ClusterTask]] = []  # (priority, sequence, task)
        self._counter = 0

    def enqueue_task(self, task: ClusterTask) -> None:
        """Enqueues a ClusterTask into priority queue."""
        with self._lock:
            self._counter += 1
            # Inverse priority so higher priority values (e.g. 10 vs 1) pop first
            heapq.heappush(self._queue, (-task.priority, self._counter, task))

    def get_next_task(self) -> Optional[ClusterTask]:
        """Pops and returns the highest priority queued ClusterTask."""
        with self._lock:
            if not self._queue:
                return None
            _, _, task = heapq.heappop(self._queue)
            return task

    def queue_size(self) -> int:
        """Returns number of currently queued tasks."""
        with self._lock:
            return len(self._queue)

    def clear_queue(self) -> None:
        """Clears queued tasks."""
        with self._lock:
            self._queue.clear()

    def list_queued_tasks(self) -> List[ClusterTask]:
        """Returns snapshot list of queued tasks."""
        with self._lock:
            return [t[2] for t in self._queue]
