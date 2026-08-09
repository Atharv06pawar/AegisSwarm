"""
AegisSwarm Attack Execution Engine package.
"""

from execution.executor import AttackExecutor
from execution.session import ExecutionSession
from execution.metrics import ExecutionMetrics
from execution.history import ExecutionHistory
from execution.persistence import ExecutionPersistence
from execution.models import ExecutionRequest, ExecutionResult
from execution.exceptions import (
    ExecutionError,
    ExecutionTimeout,
    ExecutionPersistenceError,
    ExecutionSessionError,
    ProviderExecutionError
)

__all__ = [
    "AttackExecutor",
    "ExecutionSession",
    "ExecutionMetrics",
    "ExecutionHistory",
    "ExecutionPersistence",
    "ExecutionRequest",
    "ExecutionResult",
    "ExecutionError",
    "ExecutionTimeout",
    "ExecutionPersistenceError",
    "ExecutionSessionError",
    "ProviderExecutionError"
]
