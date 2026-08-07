import importlib
import pkgutil
import inspect
import logging
from typing import Dict, Type, List

from core.plugin_base import BaseDatasetPlugin

logger = logging.getLogger(__name__)

class PluginRegistryError(Exception):
    """Custom exception for errors during plugin registration or discovery."""
    pass

class PluginRegistry:
    """
    Centralized registry for managing AegisSwarm dataset plugins.
    Handles dynamic discovery, auto-registration, and duplication checks.
    """
    
    # Stores registered plugins mapping dataset_id -> Plugin Class
    _plugins: Dict[str, Type[BaseDatasetPlugin]] = {}

    @classmethod
    def register(cls, plugin_class: Type[BaseDatasetPlugin]) -> None:
        """
        Manually registers a dataset plugin class.
        
        Args:
            plugin_class: The class inheriting from BaseDatasetPlugin to register.
            
        Raises:
            PluginRegistryError: If the plugin does not inherit from BaseDatasetPlugin,
                                 cannot be instantiated, or shares an ID with an existing plugin.
        """
        if not issubclass(plugin_class, BaseDatasetPlugin) or plugin_class is BaseDatasetPlugin:
            raise PluginRegistryError(f"Plugin {plugin_class.__name__} must inherit from BaseDatasetPlugin.")
            
        # Instantiate the plugin briefly to extract the dataset_id property
        try:
            plugin_instance = plugin_class()
            dataset_id = plugin_instance.dataset_id
        except TypeError as e:
            raise PluginRegistryError(
                f"Cannot instantiate {plugin_class.__name__}. Ensure all abstract methods "
                f"are fully implemented. Details: {e}"
            )
        
        if dataset_id in cls._plugins:
            existing_class = cls._plugins[dataset_id]
            # If it's the exact same class being re-registered, ignore it.
            if existing_class is not plugin_class:
                raise PluginRegistryError(
                    f"Duplicate dataset_id detected! '{dataset_id}' is already registered "
                    f"by {existing_class.__name__}, but {plugin_class.__name__} also claims it."
                )
            return
            
        cls._plugins[dataset_id] = plugin_class
        logger.debug(f"Successfully registered plugin: {dataset_id} ({plugin_class.__name__})")

    @classmethod
    def discover(cls, package_path: str = "plugins.datasets") -> None:
        """
        Dynamically imports all modules within the given package path
        and automatically registers classes inheriting from BaseDatasetPlugin.
        
        Args:
            package_path (str): Python dot-notation path to the plugins directory.
        """
        try:
            module = importlib.import_module(package_path)
        except ImportError as e:
            raise PluginRegistryError(f"Could not locate or import plugin package '{package_path}': {e}")

        # Iterate over all files/modules inside the plugins.datasets package
        if hasattr(module, '__path__'):
            for _, name, is_pkg in pkgutil.iter_modules(module.__path__, module.__name__ + "."):
                try:
                    sub_module = importlib.import_module(name)
                except Exception as e:
                    logger.warning(f"Failed to import plugin module {name}: {e}")
                    continue
                
                # Inspect the module for classes
                for item_name, item in inspect.getmembers(sub_module, inspect.isclass):
                    # Register valid subclasses
                    if issubclass(item, BaseDatasetPlugin) and item is not BaseDatasetPlugin:
                        # Ensure the class is actually defined in the sub_module to prevent 
                        # re-registering base classes imported into the file.
                        if item.__module__ == sub_module.__name__:
                            cls.register(item)

    @classmethod
    def get_plugin(cls, dataset_id: str) -> Type[BaseDatasetPlugin]:
        """
        Retrieves the plugin class associated with the given dataset_id.
        
        Args:
            dataset_id (str): The unique ID of the dataset to retrieve.
            
        Returns:
            Type[BaseDatasetPlugin]: The plugin class.
            
        Raises:
            PluginRegistryError: If the dataset_id is not registered.
        """
        if dataset_id not in cls._plugins:
            raise PluginRegistryError(f"Plugin for dataset_id '{dataset_id}' not found in the registry.")
        return cls._plugins[dataset_id]

    @classmethod
    def list_plugins(cls) -> List[str]:
        """
        Returns a list of all currently registered dataset IDs.
        """
        return list(cls._plugins.keys())
        
    @classmethod
    def clear(cls) -> None:
        """Clears the registry (useful for testing environments)."""
        cls._plugins.clear()
