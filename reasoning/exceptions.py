"""
Custom exception hierarchy for the AegisSwarm Semantic Reasoning & Autonomous Strategy Engine.
"""

class ReasoningError(Exception):
    """Base exception for all reasoning engine errors."""
    def __init__(self, message: str, component: str = "reasoning"):
        self.message = message
        self.component = component
        super().__init__(f"[{component}] {message}")


class MemoryError(ReasoningError):
    """Raised when reasoning memory retrieval or persistence fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Memory error: {details}", component="reasoning_memory")


class RetrievalError(ReasoningError):
    """Raised when semantic similarity retrieval fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Retrieval error: {details}", component="retrieval")


class PlannerError(ReasoningError):
    """Raised when autonomous strategic planning fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Planner error: {details}", component="planner")


class CritiqueError(ReasoningError):
    """Raised when self-critique evaluation fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Critique error: {details}", component="critique")


class ReflectionError(ReasoningError):
    """Raised when post-execution reflection fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Reflection error: {details}", component="reflection")


class RankingError(ReasoningError):
    """Raised when candidate ranking calculation fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Ranking error: {details}", component="ranking")
