"""
ExecutionHistory storage and query module for AegisSwarm Attack Execution Engine.
"""

from uuid import UUID
from typing import List, Optional
from execution.models import ExecutionResult


class ExecutionHistory:
    """
    In-memory and queryable history repository for ExecutionResult objects.
    Supports appending results, listing history, and filtering by session_id or attack_id.
    """

    def __init__(self):
        self._history: List[ExecutionResult] = []

    def append(self, result: ExecutionResult) -> None:
        """
        Appends an ExecutionResult to the history log.
        """
        self._history.append(result)

    def list(self) -> List[ExecutionResult]:
        """
        Returns all execution results in chronological order.
        """
        return list(self._history)

    def find_by_session(self, session_id: UUID) -> List[ExecutionResult]:
        """
        Returns all execution results matching a specific session UUID.
        """
        return [res for res in self._history if res.session_id == session_id]

    def find_by_attack(self, attack_id: UUID) -> List[ExecutionResult]:
        """
        Returns all execution results matching a specific source attack_id (sample_id).
        """
        return [res for res in self._history if res.attack_id == attack_id]

    def latest(self) -> Optional[ExecutionResult]:
        """
        Returns the most recently recorded ExecutionResult, or None if history is empty.
        """
        return self._history[-1] if self._history else None

    def clear(self) -> None:
        """
        Clears the in-memory history log.
        """
        self._history.clear()
