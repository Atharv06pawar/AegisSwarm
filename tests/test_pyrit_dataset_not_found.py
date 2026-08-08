import pytest
from plugins.datasets.pyrit import PyRITPlugin
from core.exceptions import DatasetNotFoundError

def test_pyrit_raises_dataset_not_found(tmp_path, monkeypatch):
    """
    Verifies that PyRITPlugin.fetch() raises DatasetNotFoundError
    when no authentic raw dataset files exist in raw/pyrit/.
    """
    plugin = PyRITPlugin()
    fake_raw = tmp_path / "raw" / "pyrit"
    fake_raw.mkdir(parents=True, exist_ok=True)
    
    # Change working directory context so fetch checks empty fake_raw
    monkeypatch.chdir(tmp_path)
    
    with pytest.raises(DatasetNotFoundError, match="Authentic PyRIT dataset file not found"):
        plugin.fetch()
