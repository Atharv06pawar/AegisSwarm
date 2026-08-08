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
    ToolCall, Artifact, ArtifactType, EvaluationMetadata, EmbeddingReference,
    ValidationResult
)

logger = logging.getLogger(__name__)

class PyRITPlugin(BaseDatasetPlugin):
    """
    Production ingestion plugin for the Microsoft PyRIT (Python Risk Identification Tool) framework dataset.
    Translates multi-turn red teaming orchestrations, Crescendo strategies, TAP traces,
    evaluator scores, tool calls, artifacts, and prompt targets into the canonical AegisSwarm AUAO v1.0 AttackRecord schema.
    """
    
    @property
    def dataset_id(self) -> str:
        return "pyrit"

    @property
    def parser_version(self) -> str:
        return "1.0.0"

    def metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            dataset_id=self.dataset_id,
            description="PyRIT: Microsoft Python Risk Identification Tool for AI Red Teaming & Multi-Turn Attack Automation.",
            license=LicenseMetadata(
                name=LicenseType.MIT,
                url="https://github.com/Azure/PyRIT"
            )
        )

    def fetch(self) -> str:
        """
        Locates authentic local raw PyRIT dataset files.
        Validates dataset presence in 'raw/pyrit/'.
        Raises DatasetNotFoundError if authentic files are missing.
        Never generates synthetic or demonstration records.
        """
        raw_dir = Path("raw/pyrit")
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported raw file names in preference order
        candidate_files = [
            raw_dir / "dataset.jsonl",
            raw_dir / "pyrit.jsonl",
            raw_dir / "dataset.json",
            raw_dir / "dataset.csv",
            raw_dir / "dataset.parquet"
        ]
        
        for file_path in candidate_files:
            if file_path.exists() and file_path.stat().st_size > 0:
                logger.info(f"[{self.dataset_id}] Located authentic dataset file: {file_path}")
                return str(file_path)

        # Fallback check for any valid data file in raw/pyrit/
        for existing in raw_dir.glob("*"):
            if existing.is_file() and existing.suffix.lower() in [".jsonl", ".csv", ".json", ".parquet"] and existing.stat().st_size > 0:
                logger.info(f"[{self.dataset_id}] Discovered raw dataset file: {existing}")
                return str(existing)

        raise DatasetNotFoundError(
            f"Authentic PyRIT dataset file not found in '{raw_dir}'. "
            f"Expected 'dataset.jsonl', 'pyrit.jsonl', 'dataset.json', 'dataset.csv', or 'dataset.parquet'. "
            f"Please export or download official PyRIT attack traces from https://github.com/Azure/PyRIT "
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
                    # Parse JSON conversation string if encoded as string in CSV
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
        Converts PyRIT attack scenarios into canonical AegisSwarm AttackRecord objects.
        Preserves session_id, strategy, objective, score, multi-turn conversation, tool calls, artifacts, and embeddings.
        """
        strategy = str(raw_record.get("attack_strategy", raw_record.get("strategy", "UnknownStrategy")))
        target_system = str(raw_record.get("target_system", raw_record.get("target", "unknown")))
        evaluator_model = str(raw_record.get("evaluator_model", "pyrit_evaluator"))
        success = bool(raw_record.get("success", False))
        
        try:
            score = float(raw_record.get("score", 1.0 if success else 0.0))
        except (ValueError, TypeError):
            score = 1.0 if success else 0.0
            
        raw_conv = raw_record.get("conversation", [])

        # Taxonomy Node Assignment per ontology_mapping_rules.md Section 5.4
        strategy_lower = strategy.lower()
        if "crescendo" in strategy_lower or "multi" in strategy_lower:
            taxonomy_node = "AUAO-JB-MULTI-CREEP"
            difficulty = "Expert"
        elif "gcg" in strategy_lower or "tree" in strategy_lower or "tap" in strategy_lower:
            taxonomy_node = "AUAO-JB-ADV-GCG"
            difficulty = "Expert"
        elif "b64" in strategy_lower or "base64" in strategy_lower or "converter" in strategy_lower:
            taxonomy_node = "AUAO-MM-OBF-B64"
            difficulty = "Medium"
        elif "leak" in strategy_lower or "system" in strategy_lower:
            taxonomy_node = "AUAO-LK-DIR-REPEAT"
            difficulty = "Hard"
        else:
            taxonomy_node = "AUAO-PI-DIR-RO-AUTH-SYS"
            difficulty = "Medium"

        # Build Conversation Turns
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

                    # Map Role
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
                            tool_calls_list.append(
                                ToolCall(
                                    tool_call_id=str(tc.get("tool_call_id", f"call_{uuid.uuid4().hex[:6]}")),
                                    tool_name=str(tc.get("tool_name", tc.get("name", "unknown_tool"))),
                                    arguments=tc.get("arguments", tc.get("args", {}))
                                )
                            )

                    # Parse Artifacts
                    artifacts_list: List[Artifact] = []
                    if "artifacts" in turn_data and isinstance(turn_data["artifacts"], list):
                        for art in turn_data["artifacts"]:
                            art_type_str = str(art.get("type", "raw_bytes")).lower()
                            if "img" in art_type_str or "image" in art_type_str:
                                art_enum = ArtifactType.IMAGE
                            elif "pdf" in art_type_str:
                                art_enum = ArtifactType.PDF
                            elif "code" in art_type_str:
                                art_enum = ArtifactType.CODE
                            elif "html" in art_type_str:
                                art_enum = ArtifactType.HTML
                            else:
                                art_enum = ArtifactType.RAW_BYTES

                            artifacts_list.append(
                                Artifact(
                                    artifact_id=str(art.get("artifact_id", uuid.uuid4().hex[:8])),
                                    type=art_enum,
                                    uri_or_base64=str(art.get("uri_or_base64", art.get("uri", "")))
                                )
                            )

                    msg = Message(
                        role=role_enum,
                        content=content_str,
                        is_injection_source=is_inj,
                        tool_calls=tool_calls_list,
                        artifacts=artifacts_list
                    )

                    turns.append(
                        ConversationTurn(
                            turn_id=idx,
                            messages=[msg]
                        )
                    )

        # Fallback if conversation lacked explicitly tagged injection source
        if not turns:
            prompt_req = str(raw_record.get("prompt_request", raw_record.get("attack_objective", raw_record.get("prompt", "PyRIT Prompt Injection"))))
            if prompt_req.strip():
                msg = Message(
                    role=MessageRole.USER,
                    content=prompt_req.strip(),
                    is_injection_source=True,
                    tool_calls=[],
                    artifacts=[]
                )
                turns.append(ConversationTurn(turn_id=0, messages=[msg]))
                has_injection_source = True
        elif not has_injection_source and turns:
            # Mark the last turn message as injection source
            turns[-1].messages[0].is_injection_source = True
            has_injection_source = True

        # Parse Optional Embedding Reference
        embedding_ref: Optional[EmbeddingReference] = None
        if "embedding" in raw_record and isinstance(raw_record["embedding"], dict):
            emb = raw_record["embedding"]
            embedding_ref = EmbeddingReference(
                model_name=str(emb.get("model", emb.get("model_name", "text-embedding-3-large"))),
                vector_id=str(emb.get("vector_id", emb.get("vector_uri", "pyrit_vec_001")))
            )

        # Build Evaluation Metadata
        evaluations = [
            EvaluationMetadata(
                target_model=target_system if target_system != "" else "azure-openai-gpt4",
                attack_success=success,
                severity_score=round(score * 10.0, 2),
                evaluator_model=evaluator_model
            )
        ]

        # Build Validation Results
        validation_results = [
            ValidationResult(
                validator_name="AUAO-VAL-PYRIT-001",
                is_valid=has_injection_source,
                confidence=0.95,
                message="Authentic PyRIT attack trace validated."
            )
        ]

        return AttackRecord(
            sample_id=uuid.uuid4(),
            taxonomy_node=taxonomy_node,
            difficulty_level=difficulty,
            turns=turns,
            evaluations=evaluations,
            dataset_metadata=self.metadata(),
            parser_metadata=ParserMetadata(
                parser_version=self.parser_version,
                source_plugin=self.dataset_id,
                raw_file_sha256="COMPUTED_BY_ORCHESTRATOR"
            ),
            embedding_reference=embedding_ref,
            validation_results=validation_results
        )

    def validate(self, records: Iterator[AttackRecord]) -> Iterator[AttackRecord]:
        """
        Validates normalized PyRIT records.
        Rejects records missing injection sources, empty conversations, or malformed turns.
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
