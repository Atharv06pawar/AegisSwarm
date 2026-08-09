"""
Custom exception hierarchy for the AegisSwarm Evaluation Engine.
"""

class EvaluationError(Exception):
    """Base exception for all Evaluation Engine errors."""
    def __init__(self, message: str, evaluator: str = "unknown"):
        self.message = message
        self.evaluator = evaluator
        super().__init__(f"[{evaluator}] {message}")


class EvaluatorNotFound(EvaluationError):
    """Raised when a requested evaluator is not registered in the evaluator registry."""
    def __init__(self, evaluator: str):
        super().__init__(message=f"Evaluator '{evaluator}' is not registered.", evaluator=evaluator)


class EvaluationConfigurationError(EvaluationError):
    """Raised when an evaluator configuration parameter or regex pattern is invalid."""
    def __init__(self, evaluator: str, details: str):
        super().__init__(message=f"Configuration error: {details}", evaluator=evaluator)


class DetectorExecutionError(EvaluationError):
    """Raised when an error occurs during evaluation execution."""
    def __init__(self, evaluator: str, details: str):
        super().__init__(message=f"Detector execution error: {details}", evaluator=evaluator)
