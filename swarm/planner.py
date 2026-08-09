"""
Swarm Planner implementations for AegisSwarm.
Maps AttackRecords in a SwarmRequest to targeted attacker agents.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any
from core.schema import AttackRecord
from swarm.models import SwarmRequest
from swarm.exceptions import PlannerError


class BasePlanner(ABC):
    """
    Abstract Base Class for Swarm Planners.
    Defines the contract for transforming a SwarmRequest into an ordered agent attack plan.
    """

    @abstractmethod
    def plan(self, request: SwarmRequest) -> List[Tuple[str, AttackRecord]]:
        """
        Generates an ordered plan of (agent_name, attack_record) tuples.
        
        Args:
            request (SwarmRequest): Swarm request container.
            
        Returns:
            List[Tuple[str, AttackRecord]]: Planned agent allocations.
        """
        pass


class SequentialPlanner(BasePlanner):
    """
    Production planner allocating AttackRecords sequentially to target attacker agents based on taxonomy nodes.
    """

    TAXONOMY_MAP = {
        "AUAO-PI-DIR": "direct_injection",
        "AUAO-PI-IND": "indirect_injection",
        "AUAO-JB": "jailbreak",
        "AUAO-TL": "tool_attack",
        "AUAO-LK": "leakage",
        "AUAO-RO": "roleplay",
        "AUAO-MT": "multi_turn"
    }

    def _select_agent_for_record(self, record: AttackRecord) -> str:
        node = record.taxonomy_node.upper()
        for prefix, agent_name in self.TAXONOMY_MAP.items():
            if prefix in node:
                return agent_name
        return "jailbreak"

    def plan(self, request: SwarmRequest) -> List[Tuple[str, AttackRecord]]:
        if not request.attack_records:
            raise PlannerError(str(request.swarm_id), "SwarmRequest contains zero AttackRecords.")

        plan_list: List[Tuple[str, AttackRecord]] = []
        for record in request.attack_records:
            agent_name = self._select_agent_for_record(record)
            plan_list.append((agent_name, record))

        return plan_list


class ParallelPlanner(BasePlanner):
    """
    Production planner supporting future-ready parallel execution batching abstractions.
    """

    def __init__(self, batch_size: int = 5):
        self.batch_size = batch_size
        self.sequential_planner = SequentialPlanner()

    def plan(self, request: SwarmRequest) -> List[Tuple[str, AttackRecord]]:
        return self.sequential_planner.plan(request)
