"""
WorkerManager module providing high-level cluster worker management and auto-scaling helpers.
"""

from typing import Optional, List
from cluster.models import WorkerNode, WorkerState
from cluster.worker import ClusterWorker
from cluster.worker_pool import WorkerPool


class WorkerManager:
    """
    Manager abstraction wrapping WorkerPool for scaling operations and lifecycle control.
    """

    def __init__(self, pool: Optional[WorkerPool] = None):
        self.pool = pool or WorkerPool()

    def add_worker(self, hostname: str = "localhost", capabilities: Optional[List[str]] = None) -> ClusterWorker:
        """Instantiates and registers a new ClusterWorker."""
        node = WorkerNode(
            hostname=hostname,
            provider_capabilities=capabilities or ["openai", "anthropic", "gemini", "ollama", "openrouter"]
        )
        worker = ClusterWorker(node=node)
        worker.start()
        self.pool.register(worker)
        return worker

    def remove_worker(self, worker_id) -> None:
        """Unregisters and shuts down a worker node."""
        self.pool.unregister(worker_id)

    def scale_cluster(self, target_worker_count: int) -> List[ClusterWorker]:
        """Scales worker cluster up or down to match target worker count."""
        current_workers = self.pool.list_workers()
        current_count = len(current_workers)

        if current_count < target_worker_count:
            for i in range(target_worker_count - current_count):
                self.add_worker(hostname=f"node-{current_count + i + 1}")
        elif current_count > target_worker_count:
            to_remove = current_workers[target_worker_count:]
            for w in to_remove:
                self.remove_worker(w.node.worker_id)

        return self.pool.list_workers()
