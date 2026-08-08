import pytest
from core.orchestrator import PipelineOrchestrator
from core.registry import PluginRegistry
from storage.data_lake import JSONLBackend

def test_pipeline_single_dataset_ingestion(temp_lake_dir, mock_plugin_class):
    """Test running single plugin ingestion through PipelineOrchestrator."""
    PluginRegistry.clear()
    PluginRegistry.register(mock_plugin_class)

    backend = JSONLBackend(base_path=str(temp_lake_dir))
    orchestrator = PipelineOrchestrator(storage_backend=backend, plugin_registry=PluginRegistry, batch_size=10)

    orchestrator.run_plugin("mock_dataset")

    assert "mock_dataset" in orchestrator.stats
    assert orchestrator.stats["mock_dataset"]["records_processed"] == 1
    assert orchestrator.stats["mock_dataset"]["batches_written"] == 1

def test_pipeline_run_all(temp_lake_dir, mock_plugin_class):
    """Test running all registered plugins sequentially."""
    PluginRegistry.clear()
    PluginRegistry.register(mock_plugin_class)

    backend = JSONLBackend(base_path=str(temp_lake_dir))
    orchestrator = PipelineOrchestrator(storage_backend=backend, plugin_registry=PluginRegistry, batch_size=5)

    stats = orchestrator.run_all()
    assert "mock_dataset" in stats
    assert stats["mock_dataset"]["records_processed"] > 0
