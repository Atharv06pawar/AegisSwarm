import pytest
from plugins.datasets.jailbreakbench import JailbreakBenchPlugin
from core.exceptions import DatasetNotFoundError

def test_jailbreakbench_raises_dataset_not_found(tmp_path, monkeypatch):
    """
    Verifies that JailbreakBenchPlugin.fetch() raises DatasetNotFoundError
    when no authentic raw dataset files exist in raw/jailbreakbench/.
    """
    plugin = JailbreakBenchPlugin()
    fake_raw = tmp_path / "raw" / "jailbreakbench"
    fake_raw.mkdir(parents=True, exist_ok=True)
    
    # Change working directory context so fetch checks empty fake_raw
    monkeypatch.chdir(tmp_path)
    
    with pytest.raises(DatasetNotFoundError, match="Authentic JailbreakBench dataset file not found"):
        plugin.fetch()
