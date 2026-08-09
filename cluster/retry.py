"""
DistributedRetryCoordinator module providing fault-tolerant retry strategies and exponential backoff.
"""

import threading
from typing import Set, Dict, Any, Optional
from uuid import UUID

from cluster.models import ClusterTask
from cluster.config import ClusterConfig


class DistributedRetryCoordinator:
    """
    Retry coordinator tracking execution attempts and calculating backoff delays.
    """

    def __init__(self, config: Optional[ClusterConfig] = None):
        self.config = config or ClusterConfig()
        self._lock = threading.RLock()
        self._execution_history: Set[str] = set()

    def should_retry(self, task: ClusterTask, error: Exception) -> bool:
        """
        Determines whether a failed ClusterTask should be retried based on retry limits.
        """
        with self._lock:
            if task.retry_count >= task.max_retries:
                return False
            return True

    def record_attempt(self, task: ClusterTask) -> None:
        """Records an execution attempt to prevent duplicate concurrent runs."""
        with self._lock:
            key = f"{task.task_id}_attempt_{task.retry_count}"
            self._execution_history.add(key)
            task.retry_count += 1

    def get_retry_delay(self, task: ClusterTask) -> float:
        """Calculates exponential backoff retry delay in seconds."""
        backoff = self.config.retry_backoff_factor ** max(0, task.retry_count - 1)
        return round(backoff, 2)
