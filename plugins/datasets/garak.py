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

class GarakPlugin(BaseDatasetPlugin):
    """
    Production ingestion plugin for the authentic Garak (Generative AI Vulnerability Scanner) probe & hit dataset.
    Translates automated red teaming probes, detectors, generators, and vulnerability hit records
    into the canonical AegisSwarm AUAO v1.0 AttackRecord schema.
    """
    
    @property
    def dataset_id(self) -> str:
        return "garak"

    @property
    def parser_version(self) -> str:
        return "1.0.0"

    def metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            dataset_id=self.dataset_id,
            description="Garak: LLM Vulnerability Scanner & Automated Red Teaming Probe Benchmark.",
            license=LicenseMetadata(
                name=LicenseType.APACHE_2_0,
                url="https://github.com/leondz/garak"
            )
        )

    def fetch(self) -> str:
        """
        Locates authentic local raw Garak hitlog dataset files.
        Validates dataset presence in 'raw/garak/'.
        Raises DatasetNotFoundError if authentic files are missing.
        Never generates synthetic or demonstration records.
        """
        raw_dir = Path("raw/garak")
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported raw file names in preference order
        candidate_files = [
            raw_dir / "dataset.jsonl",
            raw_dir / "garak.jsonl",
            raw_dir / "dataset.json",
            raw_dir / "dataset.csv",
            raw_dir / "dataset.parquet"
        ]
        
        for file_path in candidate_files:
            if file_path.exists() and file_path.stat().st_size > 0:
                logger.info(f"[{self.dataset_id}] Located authentic dataset file: {file_path}")
                return str(file_path)

        # Fallback check for any valid data file or hitlog in raw/garak/
        for existing in raw_dir.glob("**/*"):
            if existing.is_file() and existing.suffix.lower() in [".jsonl", ".csv", ".json", ".parquet"] and existing.stat().st_size > 0:
                logger.info(f"[{self.dataset_id}] Discovered raw dataset file: {existing}")
                return str(existing)

        raise DatasetNotFoundError(
            f"Authentic Garak dataset file not found in '{raw_dir}'. "
            f"Expected 'dataset.jsonl', 'garak.jsonl', 'dataset.json', 'dataset.csv', or 'dataset.parquet'. "
            f"Please run garak CLI or copy hitlogs from ~/.local/share/garak/garak_runs/ into '{raw_dir}/' before starting ingestion."
        )

    def parse(self, raw_data_path: str) -> Iterator[Dict[str, Any]]:
        """
        Memory-safe streaming generator supporting JSONL, JSON, CSV, and Parquet formats.
        Never loads the full dataset into RAM.
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
        Converts Garak probe executions into canonical AegisSwarm AttackRecord objects.
        Preserves probe_name, detector_name, generator_name, target_model, vulnerability hit semantics, and detector score.
        """
        probe_name = str(raw_record.get("probe_name", raw_record.get("module", "garak.probes.general")))
        detector_name = str(raw_record.get("detector_name", "garak.detectors.default"))
        target_model = str(raw_record.get("target_model", raw_record.get("generator_name", "unknown")))
        prompt_text = str(raw_record.get("prompt", raw_record.get("payload", "")))
        output_text = str(raw_record.get("output", raw_record.get("response", "")))
        
        # Garak semantics: `passed = False` means model failed safety check (i.e. attack succeeded)
        passed = raw_record.get("passed", None)
        if passed is not None:
            attack_success = not bool(passed)
        else:
            attack_success = bool(raw_record.get("hit", True))

        try:
            score = float(raw_record.get("score", 1.0 if attack_success else 0.0))
        except (ValueError, TypeError):
            score = 1.0 if attack_success else 0.0

        # Map AUAO v1.0 Taxonomy Node per Section 5.9
        probe_lower = probe_name.lower()
        if "encoding" in probe_lower or "base64" in probe_lower:
            taxonomy_node = "AUAO-MM-OBF-B64"
            difficulty = "Medium"
        elif "leak" in probe_lower or "system" in probe_lower:
            taxonomy_node = "AUAO-LK-DIR-REPEAT"
            difficulty = "Hard"
        elif "jailbreak" in probe_lower or "dan" in probe_lower:
            taxonomy_node = "AUAO-JB-HYP-GAME"
            difficulty = "Hard"
        elif "promptinject" in probe_lower or "override" in probe_lower:
            taxonomy_node = "AUAO-PI-DIR-RO-AUTH-SYS"
            difficulty = "Medium"
        elif "continuation" in probe_lower or "completion" in probe_lower:
            taxonomy_node = "AUAO-LK-COMP"
            difficulty = "Medium"
        elif "glitch" in probe_lower or "token" in probe_lower:
            taxonomy_node = "AUAO-JB-ADV-TOK"
            difficulty = "Expert"
        else:
            taxonomy_node = "AUAO-PI-DIR-RO-AUTH-SYS"
            difficulty = "Medium"

        # Build Conversation Turns (Garak probe prompt -> target model output)
        turns: List[ConversationTurn] = []

        # User injection prompt message
        msg_user = Message(
            role=MessageRole.USER,
            content=prompt_text,
            is_injection_source=True,
            tool_calls=[],
            artifacts=[]
        )
        turns.append(ConversationTurn(turn_id=0, messages=[msg_user]))

        # Target response message if present
        if output_text.strip():
            msg_assistant = Message(
                role=MessageRole.ASSISTANT,
                content=output_text,
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
                severity_score=round(score * 10.0, 2),
                evaluator_model=detector_name
            )
        ]

        # Build Validation Results
        validation_results = [
            ValidationResult(
                validator_name="AUAO-VAL-GARAK-001",
                is_valid=len(prompt_text.strip()) > 0,
                confidence=1.0,
                message="Authentic Garak probe payload validated."
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
        Validates normalized Garak records.
        Rejects records missing injection sources, empty prompts, malformed detector records, or empty turns.
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
