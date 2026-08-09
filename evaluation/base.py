"""
Abstract Base Class for AegisSwarm Evaluators.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from evaluation.models import EvaluationRequest, EvaluationResult


class BaseEvaluator(ABC):
    """
    Abstract Base Class that every AegisSwarm Evaluator must inherit.
    Defines the contract for evaluation, health checks, and metadata properties.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The unique identifier string for this evaluator (e.g. 'regex')."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Evaluator version string (e.g. '1.0.0')."""
        pass

    @property
    @abstractmethod
    def supported_attack_types(self) -> List[str]:
        """List of AUAO attack types supported by this evaluator."""
        pass

    @abstractmethod
    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        """
        Evaluates an ExecutionResult payload.
        
        Args:
            request (EvaluationRequest): Evaluation request container.
            
        Returns:
            EvaluationResult: Structured evaluation result.
        """
        pass

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """
        Executes a health check for the evaluator.
        
        Returns:
            Dict[str, Any]: Status dictionary.
        """
        pass
