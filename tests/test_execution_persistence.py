import pytest
from uuid import uuid4
from tests.test_execution_models import create_sample_attack_record
from execution.models import ExecutionRequest, ExecutionResult
from execution.persistence import ExecutionPersistence
from execution.exceptions import ExecutionPersistenceError


def test_persistence_save_and_load(tmp_path):
    """Verify append-only JSON file persistence and load by session/attack/execution ID."""
    persistence = ExecutionPersistence(base_dir=tmp_path)
    record = create_sample_attack_record()
    session_id = uuid4()
    attack_id = record.sample_id

    request = ExecutionRequest(attack_record=record, provider="openai", model="gpt-4o")
    result = ExecutionResult(
        session_id=session_id,
        attack_id=attack_id,
        provider="openai",
        model="gpt-4o",
        completion="Persisted output test"
    )

    saved_path = persistence.save_execution(request, result)
    assert saved_path.exists()
    assert f"execution_{result.execution_id}.json" in saved_path.name

    loaded_payload = persistence.load_execution(session_id, attack_id, result.execution_id)
    assert loaded_payload["request"]["provider"] == "openai"
    assert loaded_payload["result"]["completion"] == "Persisted output test"


def test_persistence_append_only_prevents_overwrite(tmp_path):
    """Verify append-only constraint prevents overwriting existing execution file."""
    persistence = ExecutionPersistence(base_dir=tmp_path)
    record = create_sample_attack_record()
    session_id = uuid4()

    request = ExecutionRequest(attack_record=record, provider="openai")
    result = ExecutionResult(
        session_id=session_id,
        attack_id=record.sample_id,
        provider="openai",
        model="gpt-4o",
        completion="First execution"
    )

    persistence.save_execution(request, result)

    # Attempting to save same result with identical execution_id must fail
    with pytest.raises(ExecutionPersistenceError, match="already exists. Overwrite strictly forbidden"):
        persistence.save_execution(request, result)


def test_persistence_list_executions(tmp_path):
    """Verify listing executions for session and across all sessions."""
    persistence = ExecutionPersistence(base_dir=tmp_path)
    record = create_sample_attack_record()
    session_1 = uuid4()
    session_2 = uuid4()

    req = ExecutionRequest(attack_record=record, provider="ollama")
    res1 = ExecutionResult(session_id=session_1, attack_id=record.sample_id, provider="ollama", model="llama3.2", completion="Out 1")
    res2 = ExecutionResult(session_id=session_1, attack_id=record.sample_id, provider="ollama", model="llama3.2", completion="Out 2")
    res3 = ExecutionResult(session_id=session_2, attack_id=record.sample_id, provider="ollama", model="llama3.2", completion="Out 3")

    persistence.save_execution(req, res1)
    persistence.save_execution(req, res2)
    persistence.save_execution(req, res3)

    session_1_records = persistence.list_executions_for_session(session_1)
    assert len(session_1_records) == 2

    all_records = persistence.list_all_executions()
    assert len(all_records) == 3
