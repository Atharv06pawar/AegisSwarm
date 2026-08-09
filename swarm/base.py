"""
Abstract Base Class for AegisSwarm Swarm Attacker Agents.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from core.schema import AttackRecord
from execution.models import ExecutionRequest, ExecutionResult
from execution.executor import AttackExecutor


class BaseSwarmAgent(ABC):
    """
    Abstract Base Class for all autonomous attacker agents in the AegisSwarm engine.
    Agents prepare attack payloads into standard ExecutionRequest objects and submit them
    to the AttackExecutor.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique string identifier for this agent (e.g. 'jailbreak')."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Agent version string (e.g. '1.0.0')."""
        pass

    @property
    @abstractmethod
    def supported_attack_types(self) -> List[str]:
        """List of AUAO attack types supported by this agent."""
        pass

    @abstractmethod
    def prepare(self, record: AttackRecord, context: Optional[Dict[str, Any]] = None) -> ExecutionRequest:
        """
        Translates an AttackRecord and context into a provider-agnostic ExecutionRequest.
        
        Args:
            record (AttackRecord): Source attack record.
            context (Optional[Dict[str, Any]]): Optional execution context / shared memory state.
            
        Returns:
            ExecutionRequest: Configured execution request model.
        """
        pass

    def execute(self, executor: AttackExecutor, request: ExecutionRequest) -> ExecutionResult:
        """
        Executes the prepared request using the provided AttackExecutor instance.
        
        Args:
            executor (AttackExecutor): Execution engine instance.
            request (ExecutionRequest): Prepared attack request.
            
        Returns:
            ExecutionResult: Standardized execution result model.
        """
        return executor.execute(request)

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """
        Executes an agent health check.
        
        Returns:
            Dict[str, Any]: Status dictionary.
        """
        pass
