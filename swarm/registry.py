"""
SwarmRegistry for dynamic discovery and registration of BaseSwarmAgent implementations.
"""

import importlib
import pkgutil
import logging
from typing import Dict, Type, List, Optional
from swarm.base import BaseSwarmAgent
from swarm.exceptions import AgentNotFound

logger = logging.getLogger(__name__)


class SwarmRegistry:
    """
    Registry class maintaining registered BaseSwarmAgent implementation classes.
    Supports manual registration, dynamic discovery from swarm/agents, and agent lookup.
    """

    _registry: Dict[str, Type[BaseSwarmAgent]] = {}

    @classmethod
    def register(cls, agent_cls: Type[BaseSwarmAgent], name: Optional[str] = None) -> None:
        """
        Registers a BaseSwarmAgent implementation class.
        
        Args:
            agent_cls (Type[BaseSwarmAgent]): The agent class inheriting from BaseSwarmAgent.
            name (Optional[str]): Optional custom name override.
        """
        if not issubclass(agent_cls, BaseSwarmAgent):
            raise TypeError(f"Class '{agent_cls.__name__}' must inherit from BaseSwarmAgent.")

        try:
            temp_name = agent_cls.name.fget(None) if isinstance(agent_cls.name, property) else name
        except Exception:
            temp_name = name or agent_cls.__name__.lower()

        final_key = (name or temp_name or agent_cls.__name__).lower()
        cls._registry[final_key] = agent_cls
        logger.info(f"Registered swarm agent: '{final_key}' ({agent_cls.__name__})")

    @classmethod
    def unregister(cls, name: str) -> None:
        """
        Unregisters a swarm agent class by name.
        """
        key = name.lower()
        if key in cls._registry:
            del cls._registry[key]
            logger.info(f"Unregistered swarm agent: '{key}'")

    @classmethod
    def clear(cls) -> None:
        """
        Clears all registered agents.
        """
        cls._registry.clear()

    @classmethod
    def discover(cls) -> List[str]:
        """
        Dynamically discovers and registers all agents in swarm/agents/.
        
        Returns:
            List[str]: Names of registered agents.
        """
        try:
            import swarm.agents as agents_pkg
            for _, module_name, _ in pkgutil.iter_modules(agents_pkg.__path__):
                full_module_name = f"swarm.agents.{module_name}"
                mod = importlib.import_module(full_module_name)
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseSwarmAgent) and attr is not BaseSwarmAgent:
                        ag_name = getattr(attr, "name", None)
                        if isinstance(ag_name, property):
                            try:
                                inst = attr()
                                ag_name = inst.name
                            except Exception:
                                ag_name = module_name
                        elif not ag_name:
                            ag_name = module_name
                        cls.register(attr, name=str(ag_name))
        except Exception as e:
            logger.warning(f"Error during swarm agent discovery: {e}")

        return cls.list_agents()

    @classmethod
    def list_agents(cls) -> List[str]:
        """
        Returns a sorted list of registered agent names.
        """
        return sorted(list(cls._registry.keys()))

    @classmethod
    def get_agent(cls, name: str) -> Type[BaseSwarmAgent]:
        """
        Retrieves the agent class by name.
        
        Raises:
            AgentNotFound: If agent name is not registered.
        """
        key = name.lower()
        if key not in cls._registry:
            if not cls._registry:
                cls.discover()
            if key not in cls._registry:
                raise AgentNotFound(name)
        return cls._registry[key]
