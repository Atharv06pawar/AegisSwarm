"""
Custom exception hierarchy for the AegisSwarm Adaptive Planning & Learning Engine.
"""

class LearningError(Exception):
    """Base exception for all learning engine errors."""
    def __init__(self, message: str, component: str = "learning"):
        self.message = message
        self.component = component
        super().__init__(f"[{component}] {message}")


class MemoryError(LearningError):
    """Raised when adaptive memory retrieval, pruning, or persistence fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Memory error: {details}", component="memory")


class PlannerError(LearningError):
    """Raised when adaptive attack plan generation fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Planner error: {details}", component="planner")


class MutationError(LearningError):
    """Raised when strategy mutation fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Mutation error: {details}", component="mutation")


class GraphError(LearningError):
    """Raised when attack graph traversal or node creation fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Attack graph error: {details}", component="graph")


class OptimizerError(LearningError):
    """Raised when strategy optimization fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Optimizer error: {details}", component="optimizer")


class ReplayError(LearningError):
    """Raised when campaign or attack replay fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Replay error: {details}", component="replay")
