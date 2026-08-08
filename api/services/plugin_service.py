from typing import List, Optional
from core.registry import PluginRegistry, PluginRegistryError
from core.plugin_base import BaseDatasetPlugin
from core.schema import DatasetMetadata

class PluginService:
    """
    Service layer component wrapping PluginRegistry.
    Encapsulates dataset plugin discovery, inspection, and retrieval logic.
    """

    def __init__(self, registry: Optional[PluginRegistry] = None):
        self.registry = registry or PluginRegistry()
        # Automatically trigger initial discovery
        try:
            self.registry.discover()
        except Exception:
            pass

    def discover_plugins(self) -> List[str]:
        """
        Triggers runtime dynamic plugin discovery.
        
        Returns:
            List[str]: List of discovered dataset ID strings.
        """
        self.registry.discover()
        return self.registry.list_plugins()

    def list_plugins(self) -> List[DatasetMetadata]:
        """
        Retrieves metadata objects for all registered plugins.
        
        Returns:
            List[DatasetMetadata]: List of plugin metadata objects.
        """
        dataset_ids = self.registry.list_plugins()
        metadata_list: List[DatasetMetadata] = []
        for dataset_id in dataset_ids:
            try:
                plugin_cls = self.registry.get_plugin(dataset_id)
                plugin_inst = plugin_cls()
                metadata_list.append(plugin_inst.metadata())
            except Exception:
                pass
        return metadata_list

    def get_plugin(self, plugin_id: str) -> Optional[BaseDatasetPlugin]:
        """
        Retrieves a registered plugin instance by its dataset ID.
        
        Args:
            plugin_id (str): The dataset identifier (e.g. 'hackaprompt').
            
        Returns:
            Optional[BaseDatasetPlugin]: The plugin instance if found, or None.
        """
        try:
            plugin_cls = self.registry.get_plugin(plugin_id)
            return plugin_cls()
        except PluginRegistryError:
            return None
        except Exception:
            return None
