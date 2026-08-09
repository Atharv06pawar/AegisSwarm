"""
Unit tests for Pydantic v2 models and state machine enum in orchestrator package.
"""

from uuid import uuid4
from orchestrator.models import (
    MissionState,
    MissionRequest,
    MissionModel,
    MissionCheckpoint,
    MissionGraphNode,
    MissionGraphEdge,
    MissionExecutionGraph,
    MissionReportModel,
    OrchestratorStatistics
)


def test_orchestrator_models_instantiation():
    req = MissionRequest(objective="Master loop audit", target_provider="openai", budget_usd=25.0)
    assert req.objective == "Master loop audit"
    assert req.target_provider == "openai"

    m = MissionModel(
        mission_id=req.mission_id,
        objective=req.objective,
        state=MissionState.CREATED,
        budget_usd=req.budget_usd
    )
    assert m.state == MissionState.CREATED

    chk = MissionCheckpoint(
        mission_id=req.mission_id,
        state=MissionState.EXECUTING,
        step_index=3,
        completed_stages=["reasoning", "campaign"]
    )
    assert chk.step_index == 3
    assert len(chk.completed_stages) == 2

    node = MissionGraphNode(node_id="n-reasoning", stage_name="reasoning", status="COMPLETED")
    edge = MissionGraphEdge(source_id="n-reasoning", target_id="n-campaign")
    graph = MissionExecutionGraph(mission_id=req.mission_id, nodes=[node], edges=[edge])

    assert len(graph.nodes) == 1
    assert len(graph.edges) == 1

    rep = MissionReportModel(
        mission_id=req.mission_id,
        objective=req.objective,
        state=MissionState.COMPLETED,
        attack_count=10,
        success_rate=0.9
    )
    assert rep.success_rate == 0.9

    stats = OrchestratorStatistics(total_missions=5, completed_missions=4)
    assert stats.total_missions == 5


def test_orchestrator_exceptions_workflow_and_json_report():
    from orchestrator.exceptions import (
        OrchestratorError, StateTransitionError, ExecutionGraphError, SchedulerError,
        DispatcherError, CheckpointError, RecoveryError, MissionError
    )
    from orchestrator.workflow import OrchestratorWorkflow
    from orchestrator.report import OrchestratorReportGenerator
    from orchestrator.execution_graph import ExecutionGraphBuilder

    assert "base" in str(OrchestratorError("base"))
    assert "state_machine" in StateTransitionError("A", "B").component
    assert "execution_graph" in ExecutionGraphError("graph").component
    assert "orchestrator_scheduler" in SchedulerError("sched").component
    assert "orchestrator_dispatcher" in DispatcherError("disp").component
    assert "checkpoint" in CheckpointError("chk").component
    assert "recovery" in RecoveryError("rec").component
    assert "mission" in MissionError("miss").component

    wf = OrchestratorWorkflow()
    req = MissionRequest(objective="Workflow test mission", target_provider="openai")
    m = wf.run_mission_workflow(req)
    assert m.state.value == "COMPLETED"

    builder = ExecutionGraphBuilder()
    graph = builder.build_default_graph(m.mission_id)
    rep_gen = OrchestratorReportGenerator()
    json_rep = rep_gen.generate_report(m, graph, format_type="json")
    assert "mission_id" in json_rep
