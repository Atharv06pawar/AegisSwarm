import pytest
from core.registry import PluginRegistry, PluginRegistryError
from core.plugin_base import BaseDatasetPlugin

def test_plugin_registration(mock_plugin_class):
    """Test manual plugin class registration."""
    PluginRegistry.clear()
    PluginRegistry.register(mock_plugin_class)

    assert "mock_dataset" in PluginRegistry.list_plugins()
    retrieved_cls = PluginRegistry.get_plugin("mock_dataset")
    assert retrieved_cls is mock_plugin_class

def test_plugin_duplicate_detection(mock_plugin_class):
    """Test that registering duplicate plugin classes with different names raises PluginRegistryError."""
    PluginRegistry.clear()
    PluginRegistry.register(mock_plugin_class)

    class DuplicatePlugin(mock_plugin_class):
        pass

    with pytest.raises(PluginRegistryError, match="Duplicate dataset_id detected"):
        PluginRegistry.register(DuplicatePlugin)

def test_invalid_plugin_registration():
    """Test that registering non-subclass objects raises PluginRegistryError."""
    class InvalidPlugin:
        pass

    with pytest.raises(PluginRegistryError):
        PluginRegistry.register(InvalidPlugin) # type: ignore

def test_get_nonexistent_plugin():
    """Test that retrieving an unregistered dataset ID raises PluginRegistryError."""
    PluginRegistry.clear()
    with pytest.raises(PluginRegistryError):
        PluginRegistry.get_plugin("nonexistent_id")

def test_plugin_discovery():
    """Test dynamic package discovery of built-in dataset plugins."""
    PluginRegistry.clear()
    PluginRegistry.discover()

    discovered = PluginRegistry.list_plugins()
    assert len(discovered) > 0
    assert "hackaprompt" in discovered
    assert "agentdojo" in discovered

def test_plugin_metadata(mock_plugin_class):
    """Test plugin metadata extraction."""
    inst = mock_plugin_class()
    meta = inst.metadata()
    assert meta.dataset_id == "mock_dataset"
    assert meta.description == "Mock Dataset for Unit Testing"
