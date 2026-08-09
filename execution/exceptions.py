"""
Custom exception hierarchy for the AegisSwarm Attack Execution Engine.
"""

class ExecutionError(Exception):
    """Base exception for all attack execution engine errors."""
    def __init__(self, message: str, execution_id: str = "unknown"):
        self.message = message
        self.execution_id = execution_id
        super().__init__(f"[{execution_id}] {message}")


class ExecutionTimeout(ExecutionError):
    """Raised when an attack execution times out."""
    def __init__(self, execution_id: str, timeout_seconds: float = 30.0):
        super().__init__(
            message=f"Attack execution timed out after {timeout_seconds} seconds.",
            execution_id=execution_id
        )


class ExecutionPersistenceError(ExecutionError):
    """Raised when writing or loading execution JSON files from outputs/executions/ fails."""
    def __init__(self, execution_id: str, details: str):
        super().__init__(
            message=f"Persistence error: {details}",
            execution_id=execution_id
        )


class ExecutionSessionError(ExecutionError):
    """Raised when session creation, loading, or state management fails."""
    def __init__(self, session_id: str, details: str):
        super().__init__(
            message=f"Session error for '{session_id}': {details}",
            execution_id=session_id
        )


class ProviderExecutionError(ExecutionError):
    """Raised when provider invocation during execution fails."""
    def __init__(self, execution_id: str, provider: str, details: str):
        super().__init__(
            message=f"Provider '{provider}' execution failed: {details}",
            execution_id=execution_id
        )
