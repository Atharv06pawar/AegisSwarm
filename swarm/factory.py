"""
SwarmFactory for creating BaseSwarmAgent instances.
"""

from swarm.base import BaseSwarmAgent
from swarm.registry import SwarmRegistry


class SwarmFactory:
    """
    Factory class capable of instantiating swarm agents by name.
    Simplifies creation of direct_injection, indirect_injection, jailbreak, tool_attack, leakage, roleplay, and multi_turn agents.
    """

    @staticmethod
    def create(agent_name: str, **kwargs) -> BaseSwarmAgent:
        """
        Creates and returns a configured BaseSwarmAgent instance.
        
        Args:
            agent_name (str): Agent identifier (e.g. 'jailbreak', 'direct_injection').
            **kwargs: Arguments passed to the agent constructor.
            
        Returns:
            BaseSwarmAgent: Configured agent instance.
            
        Example:
            agent = SwarmFactory.create("jailbreak")
        """
        agent_cls = SwarmRegistry.get_agent(agent_name)
        return agent_cls(**kwargs)
