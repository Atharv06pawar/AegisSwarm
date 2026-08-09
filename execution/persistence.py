"""
JSON Persistence engine for AegisSwarm Attack Executions.
Saves execution payloads under outputs/executions/session=<uuid>/attack=<uuid>/ execution_<id>.json.
Execution history is strictly append-only.
"""

import json
import logging
from pathlib import Path
from uuid import UUID
from typing import Dict, Any, List, Optional

from execution.models import ExecutionRequest, ExecutionResult
from execution.exceptions import ExecutionPersistenceError

logger = logging.getLogger(__name__)


class ExecutionPersistence:
    """
    Append-only persistence manager for attack executions.
    Stores execution requests, execution results, and metadata under outputs/executions/.
    """

    def __init__(self, base_dir: Path = Path("outputs/executions")):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_attack_directory(self, session_id: UUID, attack_id: UUID) -> Path:
        """
        Returns the output directory path for a specific session and attack ID.
        Path format: outputs/executions/session=<session_id>/attack=<attack_id>/
        """
        attack_dir = self.base_dir / f"session={session_id}" / f"attack={attack_id}"
        attack_dir.mkdir(parents=True, exist_ok=True)
        return attack_dir

    def save_execution(self, request: ExecutionRequest, result: ExecutionResult) -> Path:
        """
        Persists an execution record in an append-only JSON file.
        Never overwrites existing files; generates unique file per execution ID.
        
        Args:
            request (ExecutionRequest): Request model.
            result (ExecutionResult): Result model.
            
        Returns:
            Path: Path to saved JSON execution file.
        """
        try:
            attack_dir = self.get_attack_directory(result.session_id, result.attack_id)
            file_path = attack_dir / f"execution_{result.execution_id}.json"

            if file_path.exists():
                raise ExecutionPersistenceError(
                    str(result.execution_id),
                    f"Execution file '{file_path.name}' already exists. Overwrite strictly forbidden."
                )

            payload = {
                "request": json.loads(request.model_dump_json()),
                "result": json.loads(result.model_dump_json())
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)

            logger.info(f"Persisted execution {result.execution_id} to {file_path}")
            return file_path

        except Exception as e:
            if isinstance(e, ExecutionPersistenceError):
                raise
            raise ExecutionPersistenceError(str(result.execution_id), str(e)) from e

    def load_execution(self, session_id: UUID, attack_id: UUID, execution_id: UUID) -> Dict[str, Any]:
        """
        Loads a single execution payload by session_id, attack_id, and execution_id.
        """
        attack_dir = self.base_dir / f"session={session_id}" / f"attack={attack_id}"
        file_path = attack_dir / f"execution_{execution_id}.json"

        if not file_path.exists():
            raise ExecutionPersistenceError(str(execution_id), f"Execution file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_executions_for_session(self, session_id: UUID) -> List[Dict[str, Any]]:
        """
        Lists all persisted execution records for a given session UUID.
        """
        session_dir = self.base_dir / f"session={session_id}"
        records: List[Dict[str, Any]] = []

        if not session_dir.exists():
            return records

        for file_path in session_dir.glob("attack=*/*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    records.append(json.load(f))
            except Exception as err:
                logger.warning(f"Error reading execution file {file_path}: {err}")

        return records

    def list_all_executions(self) -> List[Dict[str, Any]]:
        """
        Lists all persisted execution records across all sessions.
        """
        records: List[Dict[str, Any]] = []
        for file_path in self.base_dir.glob("session=*/attack=*/*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    records.append(json.load(f))
            except Exception as err:
                logger.warning(f"Error reading execution file {file_path}: {err}")

        return records
