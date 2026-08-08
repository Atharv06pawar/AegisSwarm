import pytest
from plugins.datasets.garak import GarakPlugin
from core.exceptions import DatasetNotFoundError

def test_garak_raises_dataset_not_found(tmp_path, monkeypatch):
    """
    Verifies that GarakPlugin.fetch() raises DatasetNotFoundError
    when no authentic raw dataset files exist in raw/garak/.
    """
    plugin = GarakPlugin()
    fake_raw = tmp_path / "raw" / "garak"
    fake_raw.mkdir(parents=True, exist_ok=True)
    
    # Change working directory context so fetch checks empty fake_raw
    monkeypatch.chdir(tmp_path)
    
    with pytest.raises(DatasetNotFoundError, match="Authentic Garak dataset file not found"):
        plugin.fetch()
