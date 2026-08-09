import pytest
from uuid import uuid4
from tests.test_execution_models import create_sample_attack_record
from swarm.models import SwarmRequest, SwarmResult
from swarm.persistence import SwarmPersistence
from swarm.exceptions import SwarmError


def test_swarm_persistence_save_load_list(tmp_path):
    """Verify SwarmPersistence saving, loading, and listing of swarm manifests."""
    persistence = SwarmPersistence(base_dir=tmp_path)
    record = create_sample_attack_record()
    swarm_id = uuid4()

    req = SwarmRequest(swarm_id=swarm_id, target_provider="openai", attack_records=[record])
    res = SwarmResult(swarm_id=swarm_id, status="completed", total_attacks=1)

    path = persistence.save_swarm_result(req, res)
    assert path.exists()
    assert "swarm_manifest.json" in path.name

    loaded = persistence.load_swarm_result(swarm_id)
    assert loaded["result"]["swarm_id"] == str(swarm_id)
    assert loaded["request"]["target_provider"] == "openai"

    all_swarms = persistence.list_all_swarms()
    assert len(all_swarms) == 1


def test_swarm_persistence_load_non_existent_raises(tmp_path):
    """Verify loading a non-existent swarm_id raises SwarmError."""
    persistence = SwarmPersistence(base_dir=tmp_path)
    with pytest.raises(SwarmError, match="not found"):
        persistence.load_swarm_result(uuid4())
