import pytest
from plugins.datasets.promptinject import PromptInjectPlugin
from core.exceptions import DatasetNotFoundError

def test_promptinject_raises_dataset_not_found(tmp_path, monkeypatch):
    """
    Verifies that PromptInjectPlugin.fetch() raises DatasetNotFoundError
    when no authentic raw dataset files exist in raw/promptinject/.
    """
    plugin = PromptInjectPlugin()
    fake_raw = tmp_path / "raw" / "promptinject"
    fake_raw.mkdir(parents=True, exist_ok=True)
    
    # Change working directory context so fetch checks empty fake_raw
    monkeypatch.chdir(tmp_path)
    
    with pytest.raises(DatasetNotFoundError, match="Authentic PromptInject dataset file not found"):
        plugin.fetch()
