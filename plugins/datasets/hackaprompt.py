import csv
import json
import uuid
import logging
from pathlib import Path
from typing import Iterator, Dict, Any, List

try:
    import pandas as pd
except ImportError:
    pd = None

from core.plugin_base import BaseDatasetPlugin
from core.exceptions import DatasetNotFoundError
from core.schema import (
    AttackRecord, DatasetMetadata, ParserMetadata, 
    LicenseMetadata, LicenseType, ConversationTurn, Message, MessageRole,
    EvaluationMetadata, ValidationResult
)

logger = logging.getLogger(__name__)

class HackAPromptPlugin(BaseDatasetPlugin):
    """
    Production ingestion plugin for the authentic HackAPrompt dataset.
    Translates competition prompts, levels, model target outputs, and evaluations
    into the canonical AegisSwarm AUAO v1.0 AttackRecord schema.
    """
    
    @property
    def dataset_id(self) -> str:
        return "hackaprompt"
        
    @property
    def parser_version(self) -> str:
        return "1.0.0"

    def metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            dataset_id=self.dataset_id,
            description="HackAPrompt: Exposing Systemic Vulnerabilities of Large Language Models through a Global Prompt Hacking Competition.",
            license=LicenseMetadata(
                name=LicenseType.CC_BY_4_0,
                url="https://huggingface.co/datasets/HackAPrompt/HackAPrompt-dataset"
            )
        )

    def fetch(self) -> str:
        """
        Locates the authentic local raw HackAPrompt dataset file.
        Validates dataset presence in 'raw/hackaprompt/'.
        Raises DatasetNotFoundError if authentic files are missing.
        Never generates synthetic or demonstration records.
        """
        raw_dir = Path("raw/hackaprompt")
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported raw file names in preference order
        candidate_files = [
            raw_dir / "dataset.jsonl",
            raw_dir / "hackaprompt_dataset.jsonl",
            raw_dir / "hackaprompt.jsonl",
            raw_dir / "dataset.csv",
            raw_dir / "hackaprompt.csv",
            raw_dir / "dataset.json",
            raw_dir / "hackaprompt.json",
            raw_dir / "data.parquet"
        ]
        
        for file_path in candidate_files:
            if file_path.exists() and file_path.stat().st_size > 0:
                logger.info(f"[{self.dataset_id}] Located authentic dataset file: {file_path}")
                return str(file_path)
                
        # Also check for any .jsonl, .csv, .parquet, or .json file in raw/hackaprompt/
        for existing in raw_dir.glob("*"):
            if existing.is_file() and existing.suffix.lower() in [".jsonl", ".csv", ".json", ".parquet"] and existing.stat().st_size > 0:
                logger.info(f"[{self.dataset_id}] Discovered raw dataset file: {existing}")
                return str(existing)

        raise DatasetNotFoundError(
            f"Authentic HackAPrompt dataset file not found in '{raw_dir}'. "
            f"Expected 'dataset.jsonl', 'dataset.csv', or 'hackaprompt.json'. "
            f"Please download the official dataset from https://huggingface.co/datasets/HackAPrompt/HackAPrompt-dataset "
            f"and place the file in '{raw_dir}/' before starting ingestion."
        )

    def parse(self, raw_data_path: str) -> Iterator[Dict[str, Any]]:
        """
        Memory-safe streaming generator supporting JSONL, CSV, JSON, and Parquet.
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
        Normalizes authentic HackAPrompt dataset records into the AegisSwarm AttackRecord schema.
        Handles field variants: prompt, user_input, completion, expected, model, level, score, is_hack.
        """
        # Extract prompt content
        prompt = str(raw_record.get("prompt", raw_record.get("user_input", raw_record.get("user_prompt", "")))).strip()
        completion = str(raw_record.get("completion", raw_record.get("model_output", raw_record.get("response", "")))).strip()
        target_model = str(raw_record.get("model", raw_record.get("target_model", raw_record.get("model_name", "unknown")))).strip()
        
        # Parse level (1 to 10)
        raw_level = raw_record.get("level", raw_record.get("challenge_level", "1"))
        try:
            level_int = int(raw_level)
            difficulty_level = f"Level {level_int}"
        except (ValueError, TypeError):
            difficulty_level = f"Level {raw_level}"
            
        # Parse attack success indicator
        is_hack = raw_record.get("is_hack", raw_record.get("attack_success", raw_record.get("success", None)))
        if is_hack is not None:
            attack_success = bool(is_hack)
        else:
            # In competition dataset, presence of submission record typically implies success unless score == 0
            score_val = raw_record.get("score", 1.0)
            try:
                attack_success = float(score_val) > 0
            except (ValueError, TypeError):
                attack_success = True

        # Taxonomy Node Assignment matching AUAO v1.0 ontology/attack_taxonomy.json
        taxonomy_node = "Direct Prompt Injection"

        # Build Conversation Turns
        turns: List[ConversationTurn] = []

        # User prompt turn (injection source)
        msg_user = Message(
            role=MessageRole.USER,
            content=prompt,
            is_injection_source=True,
            tool_calls=[],
            artifacts=[]
        )
        turns.append(ConversationTurn(turn_id=0, messages=[msg_user]))

        # Target response turn if present
        if completion:
            msg_assistant = Message(
                role=MessageRole.ASSISTANT,
                content=completion,
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
                severity_score=7.5 if attack_success else 2.0,
                evaluator_model="human_competition_judge"
            )
        ]

        # Build Validation Results
        validation_results = [
            ValidationResult(
                validator_name="AUAO-VAL-HACKAPROMPT-001",
                is_valid=len(prompt) > 0,
                confidence=1.0,
                message="Authentic HackAPrompt record validated."
            )
        ]

        return AttackRecord(
            sample_id=uuid.uuid4(),
            taxonomy_node=taxonomy_node,
            difficulty_level=difficulty_level,
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
        Validates normalized HackAPrompt records.
        Drops corrupted records with empty prompt text or missing injection sources.
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
                            is_valid = False
                        else:
                            has_inj = True

            if is_valid and has_inj:
                yield record
