"""
ExecutionSession manager for AegisSwarm Attack Execution Engine.
Tracks session metadata, attack counts, timestamps, and session statistics.
"""

import json
import logging
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from execution.models import ExecutionResult
from execution.exceptions import ExecutionSessionError

logger = logging.getLogger(__name__)


class ExecutionSession:
    """
    Session context maintaining state, timing, and execution counts for a batch or single attack run.
    """

    def __init__(self, session_id: Optional[UUID] = None, metadata: Optional[Dict[str, Any]] = None):
        self.session_id: UUID = session_id or uuid4()
        self.created_at: str = datetime.now(timezone.utc).isoformat()
        self.closed_at: Optional[str] = None
        self.metadata: Dict[str, Any] = metadata or {}
        
        self.executed_attacks: List[str] = []
        self.total_executions: int = 0
        self.total_tokens: int = 0
        self.total_cost: float = 0.0
        self._is_closed: bool = False

    @classmethod
    def create(cls, metadata: Optional[Dict[str, Any]] = None) -> "ExecutionSession":
        """
        Factory method creating a new active ExecutionSession instance.
        """
        session = cls(metadata=metadata)
        logger.info(f"Created ExecutionSession: {session.session_id}")
        return session

    def record_execution(self, result: ExecutionResult) -> None:
        """
        Records an execution result into the current session state.
        """
        if self._is_closed:
            raise ExecutionSessionError(str(self.session_id), "Cannot record execution on a closed session.")

        attack_str = str(result.attack_id)
        if attack_str not in self.executed_attacks:
            self.executed_attacks.append(attack_str)

        self.total_executions += 1
        self.total_tokens += result.total_tokens
        self.total_cost += result.estimated_cost

    def save(self, base_dir: Path = Path("outputs/executions")) -> Path:
        """
        Saves session state manifest under outputs/executions/session=<uuid>/session_manifest.json.
        """
        session_dir = Path(base_dir) / f"session={self.session_id}"
        session_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = session_dir / "session_manifest.json"

        data = {
            "session_id": str(self.session_id),
            "created_at": self.created_at,
            "closed_at": self.closed_at,
            "metadata": self.metadata,
            "executed_attacks": self.executed_attacks,
            "total_executions": self.total_executions,
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 6),
            "is_closed": self._is_closed
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return manifest_path

    @classmethod
    def load(cls, session_id: UUID, base_dir: Path = Path("outputs/executions")) -> "ExecutionSession":
        """
        Loads an existing ExecutionSession from session_manifest.json.
        """
        manifest_path = Path(base_dir) / f"session={session_id}" / "session_manifest.json"
        if not manifest_path.exists():
            raise ExecutionSessionError(str(session_id), f"Session manifest not found at {manifest_path}")

        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        session = cls(session_id=UUID(data["session_id"]), metadata=data.get("metadata", {}))
        session.created_at = data.get("created_at", session.created_at)
        session.closed_at = data.get("closed_at")
        session.executed_attacks = data.get("executed_attacks", [])
        session.total_executions = data.get("total_executions", 0)
        session.total_tokens = data.get("total_tokens", 0)
        session.total_cost = data.get("total_cost", 0.0)
        session._is_closed = data.get("is_closed", False)

        return session

    def close(self, base_dir: Path = Path("outputs/executions")) -> None:
        """
        Closes the session, sets closed_at timestamp, and saves final session manifest.
        """
        if not self._is_closed:
            self._is_closed = True
            self.closed_at = datetime.now(timezone.utc).isoformat()
            self.save(base_dir=base_dir)
            logger.info(f"Closed ExecutionSession: {self.session_id}")
