import pytest
from uuid import uuid4
from execution.session import ExecutionSession
from execution.models import ExecutionResult
from execution.exceptions import ExecutionSessionError


def test_session_create_and_record():
    """Verify session creation and attack execution tracking."""
    session = ExecutionSession.create(metadata={"campaign_id": "c_123"})
    assert session.session_id is not None
    assert session.metadata["campaign_id"] == "c_123"
    assert session.total_executions == 0

    res = ExecutionResult(
        session_id=session.session_id,
        attack_id=uuid4(),
        provider="openai",
        model="gpt-4o",
        completion="Sample output",
        total_tokens=100,
        estimated_cost=0.002
    )

    session.record_execution(res)
    assert session.total_executions == 1
    assert session.total_tokens == 100
    assert session.total_cost == 0.002
    assert len(session.executed_attacks) == 1


def test_session_save_and_load(tmp_path):
    """Verify session manifest saving and loading."""
    session = ExecutionSession.create(metadata={"test_key": "val"})
    manifest_path = session.save(base_dir=tmp_path)
    assert manifest_path.exists()

    loaded_session = ExecutionSession.load(session_id=session.session_id, base_dir=tmp_path)
    assert loaded_session.session_id == session.session_id
    assert loaded_session.metadata["test_key"] == "val"


def test_session_close_prevents_new_records(tmp_path):
    """Verify closing a session sets closed_at timestamp and prevents further executions."""
    session = ExecutionSession.create()
    session.close(base_dir=tmp_path)
    assert session._is_closed is True
    assert session.closed_at is not None

    res = ExecutionResult(
        session_id=session.session_id,
        attack_id=uuid4(),
        provider="openai",
        model="gpt-4o",
        completion="Test"
    )

    with pytest.raises(ExecutionSessionError, match="Cannot record execution on a closed session"):
        session.record_execution(res)
