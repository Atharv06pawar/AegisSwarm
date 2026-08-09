"""
FastAPI Router for Semantic Reasoning & Autonomous Strategy Engine endpoints.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException

from reasoning.models import (
    ReasoningRequest,
    ReasoningResponse,
    StrategyCandidate,
    ReflectionResult,
    CritiqueResult,
    ReasoningMemoryRecord,
    ReasoningStatistics
)
from reasoning.planner import AutonomousPlanner
from reasoning.strategist import AutonomousStrategist
from reasoning.memory import ReasoningMemory
from api.dependencies import (
    get_autonomous_planner,
    get_autonomous_strategist,
    get_reasoning_memory,
    get_learning_memory
)
from learning.memory import LearningMemory

reasoning_router = APIRouter(prefix="/reasoning", tags=["Semantic Reasoning Engine"])


@reasoning_router.get("/status", response_model=ReasoningStatistics)
def get_reasoning_status(
    memory: ReasoningMemory = Depends(get_reasoning_memory)
):
    """Retrieves operational status and statistics of the Reasoning Engine."""
    return memory.statistics()


@reasoning_router.get("/strategies", response_model=List[StrategyCandidate])
def get_reasoning_strategies(
    planner: AutonomousPlanner = Depends(get_autonomous_planner)
):
    """Retrieves standard candidate strategies."""
    req = ReasoningRequest(objective="Standard safety audit", target_provider="openai")
    return planner.generator.generate_candidates(req)


@reasoning_router.get("/memory", response_model=List[ReasoningMemoryRecord])
def get_reasoning_memory_records(
    limit: int = Query(default=100, ge=1, le=1000),
    memory: ReasoningMemory = Depends(get_reasoning_memory)
):
    """Retrieves reasoning memory history records."""
    return memory.history(limit=limit)


@reasoning_router.get("/history", response_model=List[ReasoningMemoryRecord])
def get_reasoning_history(
    memory: ReasoningMemory = Depends(get_reasoning_memory)
):
    """Alias for /memory returning historical reasoning passes."""
    return memory.history()


@reasoning_router.get("/reports")
def get_reasoning_reports(
    planner: AutonomousPlanner = Depends(get_autonomous_planner)
):
    """Retrieves generated markdown audit reports for recent reasoning passes."""
    req = ReasoningRequest(objective="Sample audit objective for report", target_provider="openai")
    res = planner.plan_attack(req)
    report_md = planner.report_generator.generate_report(res, format_type="markdown")
    return {"latest_report": report_md, "request_id": str(res.request_id)}


@reasoning_router.post("/plan", response_model=ReasoningResponse)
def execute_reasoning_plan(
    request: ReasoningRequest,
    planner: AutonomousPlanner = Depends(get_autonomous_planner),
    learning_memory: LearningMemory = Depends(get_learning_memory)
):
    """Executes a full autonomous reasoning pass and synthesizes an attack plan."""
    return planner.plan_attack(request=request, learning_memory=learning_memory)


@reasoning_router.post("/reflect", response_model=ReflectionResult)
def execute_reflection(
    campaign_id: Optional[str] = None,
    attack_id: Optional[str] = None,
    strategist: AutonomousStrategist = Depends(get_autonomous_strategist)
):
    """Generates post-execution reflection analysis."""
    return strategist.reflect(campaign_id=campaign_id, attack_id=attack_id)


@reasoning_router.post("/critique", response_model=CritiqueResult)
def execute_critique(
    candidate: StrategyCandidate,
    strategist: AutonomousStrategist = Depends(get_autonomous_strategist)
):
    """Evaluates self-critique scores for a candidate strategy."""
    return strategist.critique(candidate)


@reasoning_router.post("/rank", response_model=List[StrategyCandidate])
def execute_ranking(
    candidates: List[StrategyCandidate],
    strategist: AutonomousStrategist = Depends(get_autonomous_strategist)
):
    """Ranks candidates by utility score."""
    return strategist.rank(candidates)


@reasoning_router.post("/reset")
def reset_reasoning_engine(
    memory: ReasoningMemory = Depends(get_reasoning_memory)
):
    """Resets reasoning memory and cached planning state."""
    memory.clear()
    return {"status": "reset_completed", "message": "Reasoning memory cleared."}
