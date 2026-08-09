import pytest
from tests.test_execution_models import create_sample_attack_record
from execution.executor import AttackExecutor
from execution.session import ExecutionSession
from execution.persistence import ExecutionPersistence
from execution.metrics import ExecutionMetrics
from execution.history import ExecutionHistory
from execution.models import ExecutionRequest


def test_executor_successful_run(tmp_path, monkeypatch):
    """Verify AttackExecutor successfully runs an attack request using LLMFactory."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-123")
    session = ExecutionSession.create()
    persistence = ExecutionPersistence(base_dir=tmp_path)
    metrics = ExecutionMetrics()
    history = ExecutionHistory()

    executor = AttackExecutor(
        session=session,
        persistence=persistence,
        metrics=metrics,
        history=history
    )

    record = create_sample_attack_record()
    request = ExecutionRequest(
        attack_record=record,
        provider="openai",
        model="gpt-4o",
        temperature=0.5
    )

    result = executor.execute(request)
    
    assert result.session_id == session.session_id
    assert result.attack_id == record.sample_id
    assert result.provider == "openai"
    assert result.model == "gpt-4o"
    assert result.status == "completed"
    assert "[OpenAI Adapter]" in result.completion
    assert result.prompt_tokens > 0
    assert result.completion_tokens > 0

    # Verify history & metrics
    assert len(history.list()) == 1
    assert metrics.total_executions == 1
    assert session.total_executions == 1

    # Verify persistence file created
    saved = persistence.list_executions_for_session(session.session_id)
    assert len(saved) == 1
    assert saved[0]["result"]["provider"] == "openai"


def test_executor_ollama_local_run(tmp_path):
    """Verify AttackExecutor successfully runs against Ollama local provider with 0 cost."""
    session = ExecutionSession.create()
    persistence = ExecutionPersistence(base_dir=tmp_path)
    metrics = ExecutionMetrics()
    history = ExecutionHistory()

    executor = AttackExecutor(
        session=session,
        persistence=persistence,
        metrics=metrics,
        history=history
    )

    record = create_sample_attack_record()
    request = ExecutionRequest(
        attack_record=record,
        provider="ollama",
        model="llama3.2"
    )

    result = executor.execute(request)

    assert result.provider == "ollama"
    assert result.model == "llama3.2"
    assert result.status == "completed"
    assert result.estimated_cost == 0.0
    assert "[Ollama Adapter]" in result.completion


def test_executor_provider_failure_handling(tmp_path, monkeypatch):
    """Verify AttackExecutor captures provider failure gracefully in ExecutionResult."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    session = ExecutionSession.create()
    executor = AttackExecutor(session=session, persistence=ExecutionPersistence(base_dir=tmp_path))
    record = create_sample_attack_record()

    request = ExecutionRequest(attack_record=record, provider="openai", model="gpt-4o")
    result = executor.execute(request)

    assert result.status == "failed"
    assert "[Execution Error]" in result.completion


def test_executor_history_lookup(tmp_path, monkeypatch):
    """Verify history lookup methods (find_by_session, find_by_attack, latest)."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-123")
    session = ExecutionSession.create()
    executor = AttackExecutor(session=session, persistence=ExecutionPersistence(base_dir=tmp_path))
    record = create_sample_attack_record()

    req = ExecutionRequest(attack_record=record, provider="openai")
    res = executor.execute(req)

    latest = executor.history.latest()
    assert latest is not None
    assert latest.execution_id == res.execution_id

    by_session = executor.history.find_by_session(session.session_id)
    assert len(by_session) == 1

    by_attack = executor.history.find_by_attack(record.sample_id)
    assert len(by_attack) == 1
