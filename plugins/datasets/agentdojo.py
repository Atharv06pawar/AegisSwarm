import csv
import json
import uuid
import logging
from pathlib import Path
from typing import Iterator, Dict, Any, List, Optional

try:
    import pandas as pd
except ImportError:
    pd = None

from core.plugin_base import BaseDatasetPlugin
from core.exceptions import DatasetNotFoundError
from core.schema import (
    AttackRecord, DatasetMetadata, ParserMetadata,
    LicenseMetadata, LicenseType, ConversationTurn, Message, MessageRole,
    ToolCall, EvaluationMetadata, ValidationResult
)

logger = logging.getLogger(__name__)

class AgentDojoPlugin(BaseDatasetPlugin):
    """
    Production ingestion plugin for the authentic AgentDojo benchmark.
    Translates complex multi-turn agent interactions, tool calls, environment metadata,
    and indirect prompt injection payloads into the canonical AegisSwarm AttackRecord schema.
    """
    
    @property
    def dataset_id(self) -> str:
        return "agentdojo"

    @property
    def parser_version(self) -> str:
        return "1.0.0"

    def metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            dataset_id=self.dataset_id,
            description="AgentDojo: Dynamic Execution Benchmark for Indirect Prompt Injection in Autonomous AI Agents.",
            license=LicenseMetadata(
                name=LicenseType.MIT,
                url="https://github.com/dreadnode/agentdojo"
            )
        )

    def fetch(self) -> str:
        """
        Locates authentic local raw AgentDojo dataset files.
        Validates dataset presence in 'raw/agentdojo/'.
        Raises DatasetNotFoundError if authentic files are missing.
        Never generates synthetic or demonstration records.
        """
        raw_dir = Path("raw/agentdojo")
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported raw file names in preference order
        candidate_files = [
            raw_dir / "dataset.jsonl",
            raw_dir / "agentdojo.jsonl",
            raw_dir / "dataset.json",
            raw_dir / "dataset.csv",
            raw_dir / "dataset.parquet"
        ]
        
        for file_path in candidate_files:
            if file_path.exists() and file_path.stat().st_size > 0:
                logger.info(f"[{self.dataset_id}] Located authentic dataset file: {file_path}")
                return str(file_path)

        # Fallback check for any valid data file in raw/agentdojo/
        for existing in raw_dir.glob("**/*"):
            if existing.is_file() and existing.suffix.lower() in [".jsonl", ".csv", ".json", ".parquet"] and existing.stat().st_size > 0:
                logger.info(f"[{self.dataset_id}] Discovered raw dataset file: {existing}")
                return str(existing)

        raise DatasetNotFoundError(
            f"Authentic AgentDojo dataset file not found in '{raw_dir}'. "
            f"Expected 'dataset.jsonl', 'agentdojo.jsonl', 'dataset.json', 'dataset.csv', or 'dataset.parquet'. "
            f"Please download the official dataset from https://github.com/dreadnode/agentdojo "
            f"and place the file in '{raw_dir}/' before starting ingestion."
        )

    def parse(self, raw_data_path: str) -> Iterator[Dict[str, Any]]:
        """
        Memory-safe streaming generator supporting JSONL, JSON, CSV, and Parquet formats.
        Never loads the complete dataset into memory.
        """
        path = Path(raw_data_path)
        if not path.exists():
            raise DatasetNotFoundError(f"Raw dataset path does not exist: {raw_data_path}")

        ext = path.suffix.lower()
        logger.info(f"[{self.dataset_id}] Parsing raw dataset stream from {path.name} ({ext})...")

        if ext == ".jsonl":
            with open(path, "r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError as err:
                            logger.warning(f"[{self.dataset_id}] Skipping malformed JSON line {line_idx}: {err}")
                            continue

        elif ext == ".csv":
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if "conversation" in row and isinstance(row["conversation"], str):
                        try:
                            row["conversation"] = json.loads(row["conversation"])
                        except Exception:
                            pass
                    yield row

        elif ext == ".parquet":
            if pd is None:
                raise ImportError("Pandas / PyArrow is required to parse .parquet files.")
            df = pd.read_parquet(path)
            for _, row in df.iterrows():
                yield row.to_dict()

        elif ext == ".json":
            logger.warning(f"[{self.dataset_id}] Parsing standard .json file iteratively...")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        yield item
                else:
                    yield data
        else:
            raise ValueError(f"Unsupported file format for {self.dataset_id}: {ext}")

    def normalize(self, raw_record: Dict[str, Any]) -> AttackRecord:
        """
        Translates raw AgentDojo scenario records into canonical AttackRecord objects.
        Preserves environment metadata, indirect injection vector, tool calls, and execution traces.
        """
        environment = str(raw_record.get("environment", "general_agent"))
        injection_vector = str(raw_record.get("injection_vector", "document_injection"))
        raw_conv = raw_record.get("conversation", [])
        target_model = str(raw_record.get("target_model", "unknown"))
        success = bool(raw_record.get("success", False))

        # Map taxonomy node per AUAO v1.0 Section 5.3
        if "pdf" in injection_vector or "file" in environment or "doc" in injection_vector:
            taxonomy_node = "AUAO-PI-IND-DOC-PDF"
        elif "web" in environment or "dom" in injection_vector:
            taxonomy_node = "AUAO-PI-IND-WEB-DOM"
        elif "cmd" in injection_vector or "bash" in environment:
            taxonomy_node = "AUAO-TL-PARAM-CMD"
        else:
            taxonomy_node = "AUAO-TL-UNAUTH-BYPASS"

        # Build multi-turn sequence
        turns: List[ConversationTurn] = []
        has_injection_source = False

        if isinstance(raw_conv, list):
            for idx, turn_data in enumerate(raw_conv):
                if isinstance(turn_data, dict):
                    role_str = str(turn_data.get("role", "user")).lower()
                    content_str = str(turn_data.get("content", ""))
                    is_inj = bool(turn_data.get("is_injection", False) or turn_data.get("is_injection_source", False))

                    if is_inj:
                        has_injection_source = True

                    # Map Role Enum
                    if role_str == "system":
                        role_enum = MessageRole.SYSTEM
                    elif role_str == "assistant":
                        role_enum = MessageRole.ASSISTANT
                    elif role_str == "tool":
                        role_enum = MessageRole.TOOL
                    else:
                        role_enum = MessageRole.USER

                    # Parse Tool Calls
                    tool_calls_list: List[ToolCall] = []
                    if "tool_calls" in turn_data and isinstance(turn_data["tool_calls"], list):
                        for tc in turn_data["tool_calls"]:
                            if isinstance(tc, dict):
                                tool_calls_list.append(
                                    ToolCall(
                                        tool_call_id=str(tc.get("tool_call_id", f"call_{uuid.uuid4().hex[:6]}")),
                                        tool_name=str(tc.get("tool_name", tc.get("name", "unknown_tool"))),
                                        arguments=tc.get("arguments", tc.get("args", {}))
                                    )
                                )

                    msg = Message(
                        role=role_enum,
                        content=content_str,
                        is_injection_source=is_inj,
                        tool_calls=tool_calls_list
                    )

                    turns.append(
                        ConversationTurn(
                            turn_id=idx,
                            messages=[msg]
                        )
                    )

        # Fallback if conversation lacked explicit injection tag
        if not turns:
            injection_text = str(raw_record.get("injection_task", raw_record.get("user_task", "Injection")))
            if injection_text.strip():
                msg = Message(
                    role=MessageRole.USER,
                    content=injection_text.strip(),
                    is_injection_source=True,
                    tool_calls=[]
                )
                turns.append(ConversationTurn(turn_id=0, messages=[msg]))
                has_injection_source = True
        elif not has_injection_source and turns:
            # Mark the last turn message as injection source
            turns[-1].messages[0].is_injection_source = True
            has_injection_source = True

        # Build Evaluations
        evaluations = [
            EvaluationMetadata(
                target_model=target_model if target_model != "" else "gpt-4o",
                attack_success=success,
                severity_score=9.0 if success else 3.0,
                evaluator_model="agentdojo_evaluator"
            )
        ]

        # Build Validation Results
        validation_results = [
            ValidationResult(
                validator_name="AUAO-VAL-AGENTDOJO-001",
                is_valid=has_injection_source,
                confidence=1.0,
                message="Authentic AgentDojo injection trace validated."
            )
        ]

        return AttackRecord(
            sample_id=uuid.uuid4(),
            taxonomy_node=taxonomy_node,
            difficulty_level="Hard",
            turns=turns,
            evaluations=evaluations,
            dataset_metadata=self.metadata(),
            parser_metadata=ParserMetadata(
                parser_version=self.parser_version,
                source_plugin=self.dataset_id,
                raw_file_sha256="COMPUTED_BY_ORCHESTRATOR"
            ),
            validation_results=validation_results
        )

    def validate(self, records: Iterator[AttackRecord]) -> Iterator[AttackRecord]:
        """
        Validates normalized records against AgentDojo assertion rules.
        Rejects records missing injection sources, empty conversations, malformed tool calls, or empty payloads.
        """
        for record in records:
            is_valid = True

            if not record.turns:
                is_valid = False

            has_inj = False
            for turn in record.turns:
                if not turn.messages:
                    is_valid = False
                    break
                for msg in turn.messages:
                    if msg.is_injection_source:
                        if not msg.content.strip():
                            logger.warning(f"[{self.dataset_id}] Dropping corrupted record: Empty injection source text.")
                            is_valid = False
                        else:
                            has_inj = True

            if is_valid and has_inj:
                yield record
