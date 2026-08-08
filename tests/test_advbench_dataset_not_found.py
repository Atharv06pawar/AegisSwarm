import pytest
from plugins.datasets.advbench import AdvBenchPlugin
from core.exceptions import DatasetNotFoundError

def test_advbench_raises_dataset_not_found(tmp_path, monkeypatch):
    """
    Verifies that AdvBenchPlugin.fetch() raises DatasetNotFoundError
    when no authentic raw dataset files exist in raw/advbench/.
    """
    plugin = AdvBenchPlugin()
    fake_raw = tmp_path / "raw" / "advbench"
    fake_raw.mkdir(parents=True, exist_ok=True)
    
    # Change working directory context so fetch checks empty fake_raw
    monkeypatch.chdir(tmp_path)
    
    with pytest.raises(DatasetNotFoundError, match="Authentic AdvBench dataset file not found"):
        plugin.fetch()
