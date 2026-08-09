"""
ProviderRegistry for dynamic discovery and registration of LLMProvider adapters.
"""

import importlib
import pkgutil
import logging
from typing import Dict, Type, List, Optional
from providers.base import LLMProvider
from providers.exceptions import ProviderNotFound

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """
    Registry class maintaining registered LLMProvider adapter implementations.
    Supports manual registration, dynamic discovery from providers/adapters,
    and adapter instantiation.
    """

    _registry: Dict[str, Type[LLMProvider]] = {}

    @classmethod
    def register(cls, provider_cls: Type[LLMProvider], name: Optional[str] = None) -> None:
        """
        Registers an LLMProvider adapter class.
        
        Args:
            provider_cls (Type[LLMProvider]): The adapter class inheriting from LLMProvider.
            name (Optional[str]): Optional custom name override.
        """
        if not issubclass(provider_cls, LLMProvider):
            raise TypeError(f"Class '{provider_cls.__name__}' must inherit from LLMProvider.")
            
        key = (name or getattr(provider_cls, "provider_name", None) or provider_cls.__name__).lower()
        if hasattr(key, "__get__"):
            # Handle property descriptor on class
            key = provider_cls.provider_name.fget(None) if hasattr(provider_cls.provider_name, "fget") else provider_cls.__name__.lower()

        # Instantiate temporary or check property
        try:
            temp_name = provider_cls.provider_name.fget(None) if isinstance(provider_cls.provider_name, property) else name
        except Exception:
            temp_name = name or provider_cls.__name__.lower()

        final_key = (name or temp_name or provider_cls.__name__).lower()
        cls._registry[final_key] = provider_cls
        logger.info(f"Registered provider adapter: '{final_key}' ({provider_cls.__name__})")

    @classmethod
    def unregister(cls, name: str) -> None:
        """
        Unregisters a provider adapter by name.
        """
        key = name.lower()
        if key in cls._registry:
            del cls._registry[key]
            logger.info(f"Unregistered provider adapter: '{key}'")

    @classmethod
    def clear(cls) -> None:
        """
        Clears all registered adapters.
        """
        cls._registry.clear()

    @classmethod
    def discover(cls) -> List[str]:
        """
        Dynamically discovers and registers all provider adapters inside providers/adapters/.
        
        Returns:
            List[str]: Names of registered providers.
        """
        try:
            import providers.adapters as adapters_pkg
            for _, module_name, _ in pkgutil.iter_modules(adapters_pkg.__path__):
                full_module_name = f"providers.adapters.{module_name}"
                mod = importlib.import_module(full_module_name)
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if isinstance(attr, type) and issubclass(attr, LLMProvider) and attr is not LLMProvider:
                        # Extract provider name safely
                        prov_name = getattr(attr, "provider_name", None)
                        if isinstance(prov_name, property):
                            # Try dummy instantiation to read property if required
                            try:
                                inst = attr()
                                prov_name = inst.provider_name
                            except Exception:
                                prov_name = module_name
                        elif not prov_name:
                            prov_name = module_name
                        cls.register(attr, name=str(prov_name))
        except Exception as e:
            logger.warning(f"Error during provider discovery: {e}")

        return cls.list_providers()

    @classmethod
    def list_providers(cls) -> List[str]:
        """
        Returns a sorted list of registered provider names.
        """
        return sorted(list(cls._registry.keys()))

    @classmethod
    def get_provider_class(cls, name: str) -> Type[LLMProvider]:
        """
        Retrieves the provider adapter class by name.
        
        Raises:
            ProviderNotFound: If provider name is not registered.
        """
        key = name.lower()
        if key not in cls._registry:
            # Auto-discover if empty
            if not cls._registry:
                cls.discover()
            if key not in cls._registry:
                raise ProviderNotFound(name)
        return cls._registry[key]

    @classmethod
    def create(cls, provider_name: str, **kwargs) -> LLMProvider:
        """
        Instantiates a provider adapter by name.
        
        Args:
            provider_name (str): Name of the provider (e.g. 'openai', 'ollama').
            **kwargs: Arguments passed to provider constructor.
            
        Returns:
            LLMProvider: Configured adapter instance.
        """
        provider_cls = cls.get_provider_class(provider_name)
        instance = provider_cls(**kwargs)
        try:
            instance.connect()
        except Exception as e:
            logger.debug(f"[{provider_name}] Automatic connect warning during creation: {e}")
        return instance
