import pytest
from plugins.datasets.agentdojo import AgentDojoPlugin
from core.exceptions import DatasetNotFoundError

def test_agentdojo_raises_dataset_not_found(tmp_path, monkeypatch):
    """
    Verifies that AgentDojoPlugin.fetch() raises DatasetNotFoundError
    when no authentic raw dataset files exist in raw/agentdojo/.
    """
    plugin = AgentDojoPlugin()
    fake_raw = tmp_path / "raw" / "agentdojo"
    fake_raw.mkdir(parents=True, exist_ok=True)
    
    # Change working directory context so fetch checks empty fake_raw
    monkeypatch.chdir(tmp_path)
    
    with pytest.raises(DatasetNotFoundError, match="Authentic AgentDojo dataset file not found"):
        plugin.fetch()
