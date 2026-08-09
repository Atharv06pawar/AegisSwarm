"""
FastAPI Router for Master Orchestrator & Autonomous Control Plane endpoints.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query

from orchestrator.models import (
    MissionRequest,
    MissionModel,
    MissionExecutionGraph,
    OrchestratorStatistics
)
from orchestrator.coordinator import MissionCoordinator
from api.dependencies import get_mission_coordinator, get_learning_memory
from learning.memory import LearningMemory

orchestrator_router = APIRouter(prefix="/orchestrator", tags=["Master Control Plane Orchestrator"])


@orchestrator_router.get("/status", response_model=OrchestratorStatistics)
def get_orchestrator_status(
    coordinator: MissionCoordinator = Depends(get_mission_coordinator)
):
    """Retrieves operational status and summary statistics for master orchestrator."""
    return coordinator.statistics()


@orchestrator_router.get("/missions", response_model=List[MissionModel])
def get_orchestrator_missions(
    coordinator: MissionCoordinator = Depends(get_mission_coordinator)
):
    """Lists all master orchestrator missions."""
    return coordinator.list_missions()


@orchestrator_router.get("/graphs")
def get_orchestrator_graphs(
    coordinator: MissionCoordinator = Depends(get_mission_coordinator)
):
    """Retrieves DAG execution graphs for all registered missions."""
    missions = coordinator.list_missions()
    graphs = [coordinator.get_graph(m.mission_id) for m in missions if coordinator.get_graph(m.mission_id)]
    return {"total_graphs": len(graphs), "graphs": [g.model_dump(mode="json") for g in graphs]}


@orchestrator_router.get("/reports")
def get_orchestrator_reports(
    coordinator: MissionCoordinator = Depends(get_mission_coordinator)
):
    """Retrieves latest generated mission audit report."""
    missions = coordinator.list_missions()
    if not missions:
        # Create a sample completed mission for demonstration report
        req = MissionRequest(objective="Sample autonomous audit mission", target_provider="openai")
        m = coordinator.execute_mission(req)
        missions = [m]
    
    target_m = missions[0]
    g = coordinator.get_graph(target_m.mission_id)
    report_md = coordinator.report_generator.generate_report(target_m, g, format_type="markdown")
    return {"latest_report": report_md, "mission_id": str(target_m.mission_id)}


@orchestrator_router.post("/mission", response_model=MissionModel)
def execute_master_mission(
    request: MissionRequest,
    coordinator: MissionCoordinator = Depends(get_mission_coordinator),
    learning_memory: LearningMemory = Depends(get_learning_memory)
):
    """Initiates and executes complete autonomous mission loop."""
    return coordinator.execute_mission(request=request, learning_memory=learning_memory)


@orchestrator_router.post("/pause")
def pause_mission(
    mission_id: UUID,
    coordinator: MissionCoordinator = Depends(get_mission_coordinator)
):
    """Pauses an active mission."""
    m = coordinator.get_mission(mission_id)
    if not m:
        raise HTTPException(status_code=404, detail="Mission not found.")
    m_updated = coordinator.lifecycle.pause(m)
    return {"status": "paused", "mission": m_updated.model_dump(mode="json")}


@orchestrator_router.post("/resume")
def resume_mission(
    mission_id: UUID,
    coordinator: MissionCoordinator = Depends(get_mission_coordinator)
):
    """Resumes a paused mission."""
    m = coordinator.get_mission(mission_id)
    if not m:
        raise HTTPException(status_code=404, detail="Mission not found.")
    m_updated = coordinator.lifecycle.resume(m)
    return {"status": "resumed", "mission": m_updated.model_dump(mode="json")}


@orchestrator_router.post("/cancel")
def cancel_mission(
    mission_id: UUID,
    coordinator: MissionCoordinator = Depends(get_mission_coordinator)
):
    """Cancels an active mission."""
    m = coordinator.get_mission(mission_id)
    if not m:
        raise HTTPException(status_code=404, detail="Mission not found.")
    m_updated = coordinator.lifecycle.cancel(m)
    return {"status": "cancelled", "mission": m_updated.model_dump(mode="json")}


@orchestrator_router.post("/recover")
def recover_mission(
    mission_id: UUID,
    coordinator: MissionCoordinator = Depends(get_mission_coordinator)
):
    """Triggers automatic checkpoint recovery for a mission."""
    chk = coordinator.checkpoint_manager.get_latest_checkpoint(mission_id)
    recovered_state = coordinator.recovery_engine.recover_mission(mission_id, chk)
    return {"status": "recovered", "target_state": recovered_state.value}


@orchestrator_router.post("/reset")
def reset_orchestrator(
    coordinator: MissionCoordinator = Depends(get_mission_coordinator)
):
    """Resets active mission registry."""
    coordinator._missions.clear()
    coordinator._graphs.clear()
    return {"status": "reset_completed", "message": "Orchestrator mission state cleared."}
