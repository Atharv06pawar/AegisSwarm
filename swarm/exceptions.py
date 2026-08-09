"""
Custom exception hierarchy for the AegisSwarm Swarm Orchestration Engine.
"""

class SwarmError(Exception):
    """Base exception for all Swarm Orchestration Engine errors."""
    def __init__(self, message: str, swarm_id: str = "unknown"):
        self.message = message
        self.swarm_id = swarm_id
        super().__init__(f"[{swarm_id}] {message}")


class SwarmConfigurationError(SwarmError):
    """Raised when swarm configuration or parameters are invalid."""
    def __init__(self, swarm_id: str, details: str):
        super().__init__(message=f"Configuration error: {details}", swarm_id=swarm_id)


class AgentNotFound(SwarmError):
    """Raised when a requested swarm agent is not found in the registry."""
    def __init__(self, agent_name: str, swarm_id: str = "unknown"):
        super().__init__(message=f"Agent '{agent_name}' is not registered.", swarm_id=swarm_id)


class PlannerError(SwarmError):
    """Raised when the swarm planner fails to create an execution plan."""
    def __init__(self, swarm_id: str, details: str):
        super().__init__(message=f"Planner error: {details}", swarm_id=swarm_id)


class SchedulerError(SwarmError):
    """Raised when the swarm scheduler fails to build or manage an execution queue."""
    def __init__(self, swarm_id: str, details: str):
        super().__init__(message=f"Scheduler error: {details}", swarm_id=swarm_id)


class SharedMemoryError(SwarmError):
    """Raised when thread-safe shared memory access or key operations fail."""
    def __init__(self, key: str, details: str):
        super().__init__(message=f"Shared memory error for key '{key}': {details}", swarm_id=key)
