"""
ClusterWorker implementation consuming ExecutionRequests and calling AttackExecutor.
"""

import logging
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from cluster.models import WorkerNode, WorkerState, HeartbeatPayload
from cluster.exceptions import WorkerError
from execution.models import ExecutionRequest, ExecutionResult
from execution.executor import AttackExecutor

logger = logging.getLogger(__name__)


class ClusterWorker:
    """
    Cluster worker node instance executing attack requests through AttackExecutor.
    """

    def __init__(self, node: Optional[WorkerNode] = None, executor: Optional[AttackExecutor] = None):
        self.node = node or WorkerNode()
        self.executor = executor or AttackExecutor()
        self._active_tasks: Dict[str, ExecutionRequest] = {}

    def start(self) -> None:
        """Starts worker operations and sets state to ONLINE."""
        self.node.status = WorkerState.ONLINE
        self.node.last_heartbeat = datetime.now(timezone.utc).isoformat()
        logger.info(f"Started ClusterWorker '{self.node.worker_id}' ({self.node.hostname})")

    def shutdown(self) -> None:
        """Gracefully shuts down worker operations."""
        self.node.status = WorkerState.STOPPING
        self._active_tasks.clear()
        self.node.current_load = 0
        self.node.status = WorkerState.OFFLINE
        logger.info(f"Shutdown ClusterWorker '{self.node.worker_id}'")

    def heartbeat(self) -> HeartbeatPayload:
        """Emits periodic heartbeat telemetry payload."""
        self.node.last_heartbeat = datetime.now(timezone.utc).isoformat()
        return HeartbeatPayload(
            worker_id=self.node.worker_id,
            cpu_usage_pct=20.0,
            memory_usage_pct=35.0,
            active_attacks=len(self.node.active_executions),
            queue_size=0,
            provider_utilization={"openai": self.node.current_load}
        )

    def execute_attack(self, request: ExecutionRequest) -> ExecutionResult:
        """
        Executes an attack request via AttackExecutor and tracks active execution.
        """
        if self.node.status != WorkerState.ONLINE:
            raise WorkerError(str(self.node.worker_id), f"Cannot execute task in state '{self.node.status}'")

        if self.node.current_load >= self.node.maximum_capacity:
            raise WorkerError(str(self.node.worker_id), "Worker capacity exceeded")

        exec_id_str = str(getattr(request, "execution_id", uuid4()))
        self._active_tasks[exec_id_str] = request
        self.node.active_executions.append(exec_id_str)
        self.node.current_load = len(self.node.active_executions)

        try:
            result = self.executor.execute(request)
            self.report_completion(exec_id_str)
            return result
        except Exception as err:
            self.report_failure(exec_id_str, str(err))
            raise WorkerError(str(self.node.worker_id), f"Execution failed: {err}") from err

    def report_completion(self, execution_id: str) -> None:
        """Reports successful attack execution completion and updates load."""
        if execution_id in self._active_tasks:
            del self._active_tasks[execution_id]
        if execution_id in self.node.active_executions:
            self.node.active_executions.remove(execution_id)
        self.node.current_load = len(self.node.active_executions)

    def report_failure(self, execution_id: str, error: str) -> None:
        """Reports execution failure and cleans active task tracking."""
        logger.warning(f"Worker '{self.node.worker_id}' execution '{execution_id}' failed: {error}")
        self.report_completion(execution_id)
