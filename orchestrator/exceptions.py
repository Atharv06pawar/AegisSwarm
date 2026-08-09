"""
Custom exception hierarchy for AegisSwarm Autonomous Orchestrator.
"""

class OrchestratorError(Exception):
    """Base exception for all master orchestrator errors."""
    def __init__(self, message: str, component: str = "orchestrator"):
        self.message = message
        self.component = component
        super().__init__(f"[{component}] {message}")


class StateTransitionError(OrchestratorError):
    """Raised when an invalid state transition is attempted on a mission state machine."""
    def __init__(self, from_state: str, to_state: str):
        super().__init__(
            message=f"Invalid state transition from '{from_state}' to '{to_state}'.",
            component="state_machine"
        )


class ExecutionGraphError(OrchestratorError):
    """Raised when an error occurs while building or traversing the execution DAG."""
    def __init__(self, details: str):
        super().__init__(message=f"Execution graph error: {details}", component="execution_graph")


class SchedulerError(OrchestratorError):
    """Raised when orchestrator mission scheduling fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Scheduler error: {details}", component="orchestrator_scheduler")


class DispatcherError(OrchestratorError):
    """Raised when dispatching mission tasks to workers fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Dispatcher error: {details}", component="orchestrator_dispatcher")


class CheckpointError(OrchestratorError):
    """Raised when checkpoint persistence or loading fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Checkpoint error: {details}", component="checkpoint")


class RecoveryError(OrchestratorError):
    """Raised when mission recovery fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Recovery error: {details}", component="recovery")


class MissionError(OrchestratorError):
    """Raised when a mission encounters a fatal operational error."""
    def __init__(self, details: str):
        super().__init__(message=f"Mission error: {details}", component="mission")
