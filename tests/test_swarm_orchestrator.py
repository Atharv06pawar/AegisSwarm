import pytest
from tests.test_execution_models import create_sample_attack_record
from execution.executor import AttackExecutor
from execution.persistence import ExecutionPersistence
from evaluation.evaluator import EvaluationEngine
from swarm.orchestrator import SwarmOrchestrator
from swarm.models import SwarmRequest
from swarm.memory import SwarmMemory
from swarm.metrics import SwarmMetrics
from swarm.persistence import SwarmPersistence
from swarm.exceptions import SwarmError


def test_swarm_orchestrator_full_run(tmp_path, monkeypatch):
    """Verify full end-to-end SwarmOrchestrator campaign pipeline execution."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-123")

    exec_persistence = ExecutionPersistence(base_dir=tmp_path / "executions")
    executor = AttackExecutor(persistence=exec_persistence)
    evaluator_engine = EvaluationEngine()
    memory = SwarmMemory()
    metrics = SwarmMetrics()
    swarm_persistence = SwarmPersistence(base_dir=tmp_path / "swarms")

    orchestrator = SwarmOrchestrator(
        executor=executor,
        evaluator_engine=evaluator_engine,
        memory=memory,
        metrics=metrics,
        persistence=swarm_persistence
    )

    record1 = create_sample_attack_record()
    record2 = create_sample_attack_record()
    record2.taxonomy_node = "AUAO-JB-ADV-GCG"

    request = SwarmRequest(
        target_provider="openai",
        target_model="gpt-4o",
        attack_records=[record1, record2]
    )

    result = orchestrator.run_swarm(request)

    assert result.swarm_id == request.swarm_id
    assert result.status == "completed"
    assert result.total_agents == 2
    assert result.completed_agents == 2
    assert result.failed_agents == 0
    assert len(result.execution_ids) == 2
    assert len(result.evaluation_ids) == 2
    assert len(result.agent_results) == 2

    # Verify memory tracking
    completed_in_mem = memory.get("completed_attacks")
    failed_in_mem = memory.get("failed_attacks")
    assert len(completed_in_mem) + len(failed_in_mem) == 2

    # Verify persistence manifest
    loaded_manifest = swarm_persistence.load_swarm_result(request.swarm_id)
    assert loaded_manifest["result"]["swarm_id"] == str(request.swarm_id)
