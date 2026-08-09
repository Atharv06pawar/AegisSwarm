"""
AegisSwarm Evaluation Engine package.
"""

from evaluation.base import BaseEvaluator
from evaluation.evaluator import EvaluationEngine
from evaluation.registry import EvaluatorRegistry
from evaluation.factory import EvaluationFactory
from evaluation.models import EvaluationRequest, EvaluationResult, EvaluationSummary
from evaluation.metrics import EvaluationMetrics
from evaluation.report import EvaluationReportGenerator
from evaluation.exceptions import (
    EvaluationError,
    EvaluatorNotFound,
    EvaluationConfigurationError,
    DetectorExecutionError
)

__all__ = [
    "BaseEvaluator",
    "EvaluationEngine",
    "EvaluatorRegistry",
    "EvaluationFactory",
    "EvaluationRequest",
    "EvaluationResult",
    "EvaluationSummary",
    "EvaluationMetrics",
    "EvaluationReportGenerator",
    "EvaluationError",
    "EvaluatorNotFound",
    "EvaluationConfigurationError",
    "DetectorExecutionError"
]
