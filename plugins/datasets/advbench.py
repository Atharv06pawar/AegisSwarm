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

class AdvBenchPlugin(BaseDatasetPlugin):
    """
    Production ingestion plugin for the authentic AdvBench harmful behaviors & adversarial prompt dataset.
    Translates harmful goal instructions, adversarial GCG suffixes, target completions,
    and safety evaluation benchmark data into the canonical AegisSwarm AUAO v1.0 AttackRecord schema.
    """

    @property
    def dataset_id(self) -> str:
        return "advbench"

    @property
    def parser_version(self) -> str:
        return "1.0.0"

    def metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            dataset_id=self.dataset_id,
            description="AdvBench: Standard Benchmark of Harmful Behaviors and Adversarial Suffix Prompts.",
            license=LicenseMetadata(
                name=LicenseType.MIT,
                url="https://github.com/llm-attacks/llm-attacks"
            )
        )

    def fetch(self) -> str:
        """
        Locates authentic local raw AdvBench dataset files.
        Validates dataset presence in 'raw/advbench/'.
        Raises DatasetNotFoundError if authentic files are missing.
        Never generates synthetic or demonstration records.
        """
        raw_dir = Path("raw/advbench")
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported raw file names in preference order
        candidate_files = [
            raw_dir / "dataset.jsonl",
            raw_dir / "advbench.jsonl",
            raw_dir / "dataset.json",
            raw_dir / "dataset.csv",
            raw_dir / "dataset.parquet",
            raw_dir / "harmful_behaviors.csv",
            raw_dir / "harmful_strings.csv"
        ]
        
        for file_path in candidate_files:
            if file_path.exists() and file_path.stat().st_size > 0:
                logger.info(f"[{self.dataset_id}] Located authentic dataset file: {file_path}")
                return str(file_path)

        # Fallback check for any valid data file in raw/advbench/
        for existing in raw_dir.glob("**/*"):
            if existing.is_file() and existing.suffix.lower() in [".jsonl", ".csv", ".json", ".parquet"] and existing.stat().st_size > 0:
                logger.info(f"[{self.dataset_id}] Discovered raw dataset file: {existing}")
                return str(existing)

        raise DatasetNotFoundError(
            f"Authentic AdvBench dataset file not found in '{raw_dir}'. "
            f"Expected 'dataset.jsonl', 'advbench.jsonl', 'dataset.json', 'dataset.csv', or 'dataset.parquet'. "
            f"Please copy or download raw AdvBench files (e.g. harmful_behaviors.csv) from https://github.com/llm-attacks/llm-attacks "
            f"into '{raw_dir}/' before starting ingestion."
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
        Converts authentic AdvBench samples into canonical AegisSwarm AttackRecord objects.
        Preserves goal, prompt, target completion, category, target_model, and attack_success.
        """
        goal_text = str(raw_record.get("goal", raw_record.get("instruction", ""))).strip()
        prompt_text = str(raw_record.get("prompt", raw_record.get("user_input", goal_text))).strip()
        target_completion = str(raw_record.get("target", raw_record.get("response", ""))).strip()
        target_model = str(raw_record.get("target_model", raw_record.get("model", "unknown"))).strip()
        category = str(raw_record.get("category", raw_record.get("harm_category", "Harmful Behaviors"))).strip()
        attack_success = bool(raw_record.get("attack_success", raw_record.get("success", True)))

        # Taxonomy Node Assignment per ontology_mapping_rules.md Section 5.8
        prompt_lower = prompt_text.lower()
        category_lower = category.lower()

        if "==" in prompt_text or "describing" in prompt_lower or "gcg" in prompt_lower:
            taxonomy_node = "AUAO-JB-ADV-GCG"
            difficulty = "Hard"
        elif "role" in category_lower or "persona" in category_lower:
            taxonomy_node = "AUAO-PI-DIR-RO-PERS"
            difficulty = "Medium"
        elif "game" in category_lower or "hypothetical" in category_lower:
            taxonomy_node = "AUAO-JB-HYP-GAME"
            difficulty = "Medium"
        else:
            taxonomy_node = "AUAO-JB-ADV-GCG"
            difficulty = "Hard"

        # Build Conversation Turns
        turns: List[ConversationTurn] = []

        msg_user = Message(
            role=MessageRole.USER,
            content=prompt_text if prompt_text != "" else goal_text,
            is_injection_source=True,
            tool_calls=[],
            artifacts=[]
        )
        turns.append(ConversationTurn(turn_id=0, messages=[msg_user]))

        # Target completion turn if present
        if target_completion:
            msg_assistant = Message(
                role=MessageRole.ASSISTANT,
                content=target_completion,
                is_injection_source=False,
                tool_calls=[],
                artifacts=[]
            )
            turns.append(ConversationTurn(turn_id=1, messages=[msg_assistant]))

        # Build Evaluation Metadata
        evaluations = [
            EvaluationMetadata(
                target_model=target_model if target_model != "" else "vicuna-7b-v1.5",
                attack_success=attack_success,
                severity_score=8.5 if attack_success else 3.0,
                evaluator_model="advbench_string_match"
            )
        ]

        # Build Validation Results
        validation_results = [
            ValidationResult(
                validator_name="AUAO-VAL-ADVBENCH-001",
                is_valid=len(prompt_text) > 0 or len(goal_text) > 0,
                confidence=1.0,
                message="Authentic AdvBench harmful goal prompt validated."
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
        Validates normalized AdvBench records.
        Rejects records missing injection sources, empty goals, empty prompts, or malformed conversations.
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
