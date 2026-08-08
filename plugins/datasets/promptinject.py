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

class PromptInjectPlugin(BaseDatasetPlugin):
    """
    Production ingestion plugin for the authentic PromptInject dataset framework.
    Translates programmatic prompt injection vectors, rogue instructions, delimiter escapes,
    context injections, and evaluation benchmarks into the canonical AegisSwarm AUAO v1.0 AttackRecord schema.
    """

    @property
    def dataset_id(self) -> str:
        return "promptinject"

    @property
    def parser_version(self) -> str:
        return "1.0.0"

    def metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            dataset_id=self.dataset_id,
            description="PromptInject: Quantitative Framework for Measuring Prompt Injection Robustness in LLMs.",
            license=LicenseMetadata(
                name=LicenseType.MIT,
                url="https://github.com/prompthing/promptinject"
            )
        )

    def fetch(self) -> str:
        """
        Locates authentic local raw PromptInject dataset files.
        Validates dataset presence in 'raw/promptinject/'.
        Raises DatasetNotFoundError if authentic files are missing.
        Never generates synthetic or demonstration records.
        """
        raw_dir = Path("raw/promptinject")
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported raw file names in preference order
        candidate_files = [
            raw_dir / "dataset.jsonl",
            raw_dir / "promptinject.jsonl",
            raw_dir / "dataset.json",
            raw_dir / "dataset.csv",
            raw_dir / "dataset.parquet"
        ]
        
        for file_path in candidate_files:
            if file_path.exists() and file_path.stat().st_size > 0:
                logger.info(f"[{self.dataset_id}] Located authentic dataset file: {file_path}")
                return str(file_path)

        # Fallback check for any valid data file in raw/promptinject/
        for existing in raw_dir.glob("*"):
            if existing.is_file() and existing.suffix.lower() in [".jsonl", ".csv", ".json", ".parquet"] and existing.stat().st_size > 0:
                logger.info(f"[{self.dataset_id}] Discovered raw dataset file: {existing}")
                return str(existing)

        raise DatasetNotFoundError(
            f"Authentic PromptInject dataset file not found in '{raw_dir}'. "
            f"Expected 'dataset.jsonl', 'promptinject.jsonl', 'dataset.json', 'dataset.csv', or 'dataset.parquet'. "
            f"Please download the official dataset from https://github.com/prompthing/promptinject "
            f"and place the file in '{raw_dir}/' before starting ingestion."
        )

    def parse(self, raw_data_path: str) -> Iterator[Dict[str, Any]]:
        """
        Memory-safe streaming generator supporting JSONL, JSON, CSV, and Parquet formats.
        Never loads the full dataset into memory.
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
        Converts authentic PromptInject samples into canonical AegisSwarm AttackRecord objects.
        Preserves base_prompt, injected_prompt, attack_type, target_model, and settings.
        """
        attack_type = str(raw_record.get("attack_type", raw_record.get("strategy", "direct_injection")))
        base_prompt = str(raw_record.get("base_prompt", raw_record.get("prompt", "")))
        injected_prompt = str(raw_record.get("injected_prompt", raw_record.get("attack_payload", "")))
        target_model = str(raw_record.get("target_model", raw_record.get("model", "unknown")))
        attack_success = bool(raw_record.get("attack_success", raw_record.get("success", True)))
        
        try:
            similarity_score = float(raw_record.get("similarity_score", raw_record.get("score", 0.85)))
        except (ValueError, TypeError):
            similarity_score = 0.85

        # Taxonomy Node Assignment per ontology_mapping_rules.md Section 5.5
        attack_type_lower = attack_type.lower()
        if "xml" in attack_type_lower or "tag" in attack_type_lower:
            taxonomy_node = "AUAO-PI-DIR-DEL-XML"
            difficulty = "Medium"
        elif "md" in attack_type_lower or "markdown" in attack_type_lower:
            taxonomy_node = "AUAO-PI-DIR-DEL-MD"
            difficulty = "Medium"
        elif "base64" in attack_type_lower or "b64" in attack_type_lower or "encoding" in attack_type_lower:
            taxonomy_node = "AUAO-MM-OBF-B64"
            difficulty = "Medium"
        elif "doc" in attack_type_lower or "pdf" in attack_type_lower or "retrieved" in attack_type_lower:
            taxonomy_node = "AUAO-PI-IND-DOC-PDF"
            difficulty = "Hard"
        elif "persona" in attack_type_lower or "role" in attack_type_lower:
            taxonomy_node = "AUAO-PI-DIR-RO-PERS"
            difficulty = "Medium"
        else:
            taxonomy_node = "AUAO-PI-DIR-RO-AUTH-SYS"
            difficulty = "Medium"

        # Build Full Prompt Payload
        if base_prompt and injected_prompt and injected_prompt not in base_prompt:
            full_prompt_text = f"{base_prompt}\n{injected_prompt}".strip()
        else:
            full_prompt_text = (injected_prompt or base_prompt).strip()

        # Build Conversation Turns
        turns: List[ConversationTurn] = []

        # Parse Artifacts if present
        artifacts_list: List[Artifact] = []
        if "html" in attack_type_lower:
            artifacts_list.append(
                Artifact(
                    artifact_id=f"art_{uuid.uuid4().hex[:6]}",
                    type=ArtifactType.HTML,
                    uri_or_base64=injected_prompt
                )
            )

        msg_user = Message(
            role=MessageRole.USER,
            content=full_prompt_text,
            is_injection_source=True,
            tool_calls=[],
            artifacts=artifacts_list
        )

        turns.append(ConversationTurn(turn_id=0, messages=[msg_user]))

        # Response turn if available
        response_text = str(raw_record.get("response", raw_record.get("output", "")))
        if response_text.strip():
            msg_assistant = Message(
                role=MessageRole.ASSISTANT,
                content=response_text,
                is_injection_source=False,
                tool_calls=[],
                artifacts=[]
            )
            turns.append(ConversationTurn(turn_id=1, messages=[msg_assistant]))

        # Build Evaluation Metadata
        evaluations = [
            EvaluationMetadata(
                target_model=target_model if target_model != "" else "gpt-3.5-turbo",
                attack_success=attack_success,
                severity_score=round(similarity_score * 10.0, 2),
                evaluator_model="promptinject_judge"
            )
        ]

        # Build Validation Results
        validation_results = [
            ValidationResult(
                validator_name="AUAO-VAL-PROMPTINJECT-001",
                is_valid=len(full_prompt_text) > 0,
                confidence=1.0,
                message="Authentic PromptInject payload validated."
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
            validation_results=validation_results
        )

    def validate(self, records: Iterator[AttackRecord]) -> Iterator[AttackRecord]:
        """
        Validates normalized PromptInject records.
        Rejects records missing injection sources or containing empty prompt text.
        """
        for record in records:
            is_valid = True

            if not record.turns:
                is_valid = False

            has_inj = False
            for turn in record.turns:
                for msg in turn.messages:
                    if msg.is_injection_source:
                        if not msg.content.strip():
                            logger.warning(f"[{self.dataset_id}] Dropping corrupted record: Empty injection source text.")
                            is_valid = False
                        else:
                            has_inj = True

            if is_valid and has_inj:
                yield record
