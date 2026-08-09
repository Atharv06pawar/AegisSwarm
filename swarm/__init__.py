"""
AegisSwarm Swarm Orchestration and Adaptive Intelligence Engine package.
"""

from swarm.base import BaseSwarmAgent
from swarm.orchestrator import SwarmOrchestrator
from swarm.registry import SwarmRegistry
from swarm.factory import SwarmFactory
from swarm.memory import SwarmMemory
from swarm.metrics import SwarmMetrics
from swarm.persistence import SwarmPersistence
from swarm.planner import BasePlanner, SequentialPlanner, ParallelPlanner
from swarm.scheduler import SwarmScheduler
from swarm.models import SwarmRequest, SwarmResult, SwarmAgentResult, SwarmSummary
from swarm.exceptions import (
    SwarmError,
    SwarmConfigurationError,
    AgentNotFound,
    PlannerError,
    SchedulerError,
    SharedMemoryError
)
from swarm.strategy import StrategyType, StrategyRecommendation
from swarm.mutation import StrategyMutationEngine
from swarm.retry import RetryPolicy
from swarm.ranking import AgentRankingEngine
from swarm.intelligence import AdaptiveIntelligence
from swarm.advisor import StrategyAdvisor

__all__ = [
    "BaseSwarmAgent",
    "SwarmOrchestrator",
    "SwarmRegistry",
    "SwarmFactory",
    "SwarmMemory",
    "SwarmMetrics",
    "SwarmPersistence",
    "BasePlanner",
    "SequentialPlanner",
    "ParallelPlanner",
    "SwarmScheduler",
    "SwarmRequest",
    "SwarmResult",
    "SwarmAgentResult",
    "SwarmSummary",
    "SwarmError",
    "SwarmConfigurationError",
    "AgentNotFound",
    "PlannerError",
    "SchedulerError",
    "SharedMemoryError",
    "StrategyType",
    "StrategyRecommendation",
    "StrategyMutationEngine",
    "RetryPolicy",
    "AgentRankingEngine",
    "AdaptiveIntelligence",
    "StrategyAdvisor"
]
