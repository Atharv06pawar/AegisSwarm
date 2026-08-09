"""
Custom exception hierarchy for the AegisSwarm Distributed Worker Cluster Subsystem.
"""

class ClusterError(Exception):
    """Base exception for all cluster subsystem errors."""
    def __init__(self, message: str, component: str = "cluster"):
        self.message = message
        self.component = component
        super().__init__(f"[{component}] {message}")


class WorkerError(ClusterError):
    """Raised when worker initialization or execution fails."""
    def __init__(self, worker_id: str, details: str):
        super().__init__(message=f"Worker '{worker_id}' error: {details}", component="worker")


class WorkerNotFoundError(ClusterError):
    """Raised when a specified worker ID does not exist in the cluster pool."""
    def __init__(self, worker_id: str):
        super().__init__(message=f"Worker '{worker_id}' not found.", component="worker_pool")


class WorkerCapacityExceededError(ClusterError):
    """Raised when a worker or pool exceeds maximum capacity limits."""
    def __init__(self, details: str):
        super().__init__(message=f"Worker capacity exceeded: {details}", component="worker_pool")


class SchedulerError(ClusterError):
    """Raised when task scheduling or queueing fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Scheduler error: {details}", component="scheduler")


class DispatchError(ClusterError):
    """Raised when dispatching an execution request fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Dispatch error: {details}", component="dispatcher")


class HeartbeatError(ClusterError):
    """Raised when heartbeat monitoring or stale worker eviction fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Heartbeat error: {details}", component="heartbeat")
