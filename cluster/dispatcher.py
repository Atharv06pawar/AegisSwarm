"""
Dispatcher module routing execution requests from scheduler queue to cluster workers.
"""

import logging
from typing import Optional, Dict, Any

from cluster.models import ClusterTask
from cluster.worker_pool import WorkerPool
from cluster.load_balancer import LoadBalancer
from cluster.retry import DistributedRetryCoordinator
from cluster.exceptions import DispatchError
from execution.models import ExecutionRequest, ExecutionResult
from observability.event_bus import EventBus
from observability.events import create_telemetry_event

logger = logging.getLogger(__name__)


class Dispatcher:
    """
    Dispatcher assigning tasks to workers, executing attacks, tracking progress, and coordinating retries.
    """

    def __init__(
        self,
        pool: WorkerPool,
        load_balancer: Optional[LoadBalancer] = None,
        retry_coordinator: Optional[DistributedRetryCoordinator] = None,
        event_bus: Optional[EventBus] = None
    ):
        self.pool = pool
        self.load_balancer = load_balancer or LoadBalancer()
        self.retry_coordinator = retry_coordinator or DistributedRetryCoordinator()
        self.event_bus = event_bus or EventBus()

    def dispatch(self, task: ClusterTask, request: ExecutionRequest) -> ExecutionResult:
        """
        Selects a worker node, dispatches attack execution request, and handles completions or retries.
        """
        workers = self.pool.list_workers()
        if not workers:
            raise DispatchError("No workers registered in cluster pool.")

        worker = self.load_balancer.select_worker(workers, provider=task.provider)
        task.assigned_worker_id = worker.node.worker_id
        task.status = "DISPATCHED"

        # Emit Telemetry event
        self.event_bus.publish(
            create_telemetry_event(
                component="dispatcher",
                event_type="TaskDispatched",
                payload={"task_id": str(task.task_id), "worker_id": str(worker.node.worker_id), "provider": task.provider}
            )
        )

        try:
            self.retry_coordinator.record_attempt(task)
            result = worker.execute_attack(request)
            task.status = "COMPLETED"

            self.event_bus.publish(
                create_telemetry_event(
                    component="dispatcher",
                    event_type="TaskCompleted",
                    payload={"task_id": str(task.task_id), "execution_id": str(result.execution_id)}
                )
            )
            return result

        except Exception as err:
            task.status = "FAILED"
            self.event_bus.publish(
                create_telemetry_event(
                    component="dispatcher",
                    event_type="TaskFailed",
                    severity="ERROR",
                    payload={"task_id": str(task.task_id), "error": str(err)}
                )
            )

            if self.retry_coordinator.should_retry(task, err):
                task.status = "RETRYING"
                self.event_bus.publish(
                    create_telemetry_event(
                        component="scheduler",
                        event_type="TaskRetried",
                        payload={"task_id": str(task.task_id), "attempt": task.retry_count}
                    )
                )
                # Re-dispatch recursive retry
                return self.dispatch(task, request)

            raise DispatchError(f"Task '{task.task_id}' failed: {err}") from err
