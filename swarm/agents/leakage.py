"""
Leakage Agent for AegisSwarm.
"""

from typing import List, Dict, Any, Optional
from core.schema import AttackRecord
from execution.models import ExecutionRequest
from swarm.base import BaseSwarmAgent


class LeakageAgent(BaseSwarmAgent):
    """
    Attacker agent specializing in system prompt extraction and internal policy leakage.
    """

    @property
    def name(self) -> str:
        return "leakage"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_attack_types(self) -> List[str]:
        return ["AUAO-LK-*"]

    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "agent": self.name, "version": self.version}

    def prepare(self, record: AttackRecord, context: Optional[Dict[str, Any]] = None) -> ExecutionRequest:
        provider = context.get("target_provider", "openai") if context else "openai"
        model = context.get("target_model") if context else None

        return ExecutionRequest(
            attack_record=record,
            provider=provider,
            model=model,
            temperature=context.get("temperature", 0.7) if context else 0.7,
            metadata={"agent_name": self.name}
        )
