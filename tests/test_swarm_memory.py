import pytest
from swarm.memory import SwarmMemory
from swarm.exceptions import SharedMemoryError


def test_swarm_memory_operations():
    """Verify put, get, exists, remove, clear, and snapshot operations."""
    mem = SwarmMemory()
    
    assert mem.exists("completed_attacks") is True
    assert mem.get("completed_attacks") == []

    mem.put("custom_key", "custom_value")
    assert mem.exists("custom_key") is True
    assert mem.get("custom_key") == "custom_value"

    mem.append_to_list("completed_attacks", "attack_1")
    assert "attack_1" in mem.get("completed_attacks")

    snap = mem.snapshot()
    assert "custom_key" in snap

    mem.remove("custom_key")
    assert mem.exists("custom_key") is False

    mem.clear()
    assert mem.get("completed_attacks") == []


def test_swarm_memory_append_invalid_type_raises():
    """Verify appending to a non-list key raises SharedMemoryError."""
    mem = SwarmMemory()
    mem.put("string_key", "not_a_list")

    with pytest.raises(SharedMemoryError, match="is not a list"):
        mem.append_to_list("string_key", "item")
