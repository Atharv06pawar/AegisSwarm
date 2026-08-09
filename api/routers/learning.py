"""
FastAPI Router for Adaptive Attack Planning & Autonomous Learning Engine endpoints.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query

from learning.models import LearningMemoryRecord, AttackPlan, AttackGraphModel, ReplaySessionModel
from learning.memory import LearningMemory
from learning.planner import AdaptivePlanner
from learning.optimizer import StrategyOptimizer
from learning.replay import ReplayEngine
from learning.graph import AttackGraph
from api.dependencies import (
    get_learning_memory,
    get_adaptive_planner,
    get_strategy_optimizer,
    get_replay_engine,
    get_attack_graph
)

learning_router = APIRouter(prefix="/learning", tags=["Autonomous Learning Engine"])


@learning_router.get("")
def get_learning_overview(
    memory: LearningMemory = Depends(get_learning_memory),
    optimizer: StrategyOptimizer = Depends(get_strategy_optimizer)
):
    """Retrieves high-level learning overview and optimization state."""
    stats = memory.statistics()
    opt = optimizer.optimize(memory)
    return {
        "status": "active",
        "statistics": stats,
        "optimized_params": opt
    }


@learning_router.get("/memory", response_model=List[LearningMemoryRecord])
def get_learning_memory_records(
    limit: int = Query(default=100, ge=1, le=1000),
    memory: LearningMemory = Depends(get_learning_memory)
):
    """Retrieves historical memory records."""
    return memory.history(limit=limit)


@learning_router.get("/strategies")
def get_strategy_rankings(
    optimizer: StrategyOptimizer = Depends(get_strategy_optimizer)
):
    """Retrieves ranked mutation strategies and utility scores."""
    return optimizer.strategy_manager.get_rankings()


@learning_router.get("/graph", response_model=AttackGraphModel)
def get_attack_graph_data(
    graph: AttackGraph = Depends(get_attack_graph)
):
    """Retrieves exported AttackGraph model representation."""
    return graph.export()


@learning_router.get("/replays")
def list_replay_sessions(
    replay_engine: ReplayEngine = Depends(get_replay_engine)
):
    """Lists historical campaign replay sessions."""
    res = replay_engine.replay_campaign("campaign-sample")
    return [res.model_dump()]


@learning_router.get("/statistics")
def get_learning_statistics(
    memory: LearningMemory = Depends(get_learning_memory)
):
    """Retrieves memory summary statistics."""
    return memory.statistics()


@learning_router.post("/optimize")
def run_strategy_optimization(
    memory: LearningMemory = Depends(get_learning_memory),
    optimizer: StrategyOptimizer = Depends(get_strategy_optimizer)
):
    """Triggers strategy optimization pass over historical memory."""
    return optimizer.optimize(memory)


@learning_router.post("/replay", response_model=ReplaySessionModel)
def replay_target_campaign(
    campaign_id: str = "campaign-sample",
    replay_engine: ReplayEngine = Depends(get_replay_engine)
):
    """Executes replay reproduction for specified campaign."""
    return replay_engine.replay_campaign(campaign_id=campaign_id)


@learning_router.post("/reset")
def reset_learning_engine(
    memory: LearningMemory = Depends(get_learning_memory)
):
    """Resets learning memory records and optimization state."""
    memory.prune(max_capacity=0)
    return {"status": "reset_completed", "message": "Learning engine state reset successfully."}
