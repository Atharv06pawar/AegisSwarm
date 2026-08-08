import pytest
import shutil
from pathlib import Path
from plugins.datasets.hackaprompt import HackAPromptPlugin
from core.exceptions import DatasetNotFoundError

def test_hackaprompt_raises_dataset_not_found(tmp_path, monkeypatch):
    """
    Verifies that HackAPromptPlugin.fetch() raises DatasetNotFoundError
    when no authentic raw dataset files exist in raw/hackaprompt/.
    """
    plugin = HackAPromptPlugin()
    fake_raw = tmp_path / "raw" / "hackaprompt"
    fake_raw.mkdir(parents=True, exist_ok=True)
    
    # Change working directory context so fetch checks empty fake_raw
    monkeypatch.chdir(tmp_path)
    
    with pytest.raises(DatasetNotFoundError, match="Authentic HackAPrompt dataset file not found"):
        plugin.fetch()
