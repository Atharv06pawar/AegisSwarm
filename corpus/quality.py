import hashlib
import random
from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field, ConfigDict

from core.schema import AttackRecord
from corpus.registry import CorpusRegistry
from corpus.statistics import CorpusStatisticsCalculator

class QualityAuditReport(BaseModel):
    """
    Pydantic v2 data contract representing the quality audit report of the AegisSwarm Corpus.
    """
    model_config = ConfigDict(frozen=True)

    total_records_audited: int = Field(default=0, ge=0, description="Total records sampled and audited.")
    schema_compliance_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Rate of records adhering to Pydantic AttackRecord schema.")
    validation_pass_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Rate of records passing validation checks.")
    missing_field_counts: Dict[str, int] = Field(default_factory=dict, description="Count of records missing key fields.")
    malformed_records: int = Field(default=0, ge=0, description="Count of malformed records failing schema parsing.")
    duplicate_sample_ids: int = Field(default=0, ge=0, description="Count of duplicate sample_id UUIDs.")
    duplicate_semantic_hashes: int = Field(default=0, ge=0, description="Count of duplicate prompt payload semantic hashes.")
    annotation_confidence_average: float = Field(default=0.0, ge=0.0, le=1.0, description="Average confidence score across validation results.")
    evaluation_completeness: float = Field(default=0.0, ge=0.0, le=1.0, description="Percentage of records containing evaluation metrics.")
    parser_version_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribution of parser versions.")
    dataset_version_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribution of dataset IDs.")
    records_with_missing_taxonomy: int = Field(default=0, ge=0, description="Count of records missing valid taxonomy_node.")
    records_with_missing_evaluations: int = Field(default=0, ge=0, description="Count of records with empty evaluations.")
    records_with_missing_validation_metadata: int = Field(default=0, ge=0, description="Count of records missing validation metadata.")


class CorpusQualityAuditor:
    """
    Quality auditing engine performing memory-safe streaming verification of schema compliance,
    field completeness, duplicate Detection, annotation confidence, and validation results.
    """

    def __init__(
        self,
        registry: Optional[CorpusRegistry] = None,
        calculator: Optional[CorpusStatisticsCalculator] = None
    ):
        self.registry = registry or CorpusRegistry()
        self.calculator = calculator or CorpusStatisticsCalculator(registry=self.registry)

    def audit(self, sample_ratio: float = 1.0) -> QualityAuditReport:
        """
        Audits the entire corpus, with optional probabilistic sampling.
        
        Args:
            sample_ratio (float): Sampling ratio between 0.0 and 1.0 (default 1.0 = 100% audit).
            
        Returns:
            QualityAuditReport: Comprehensive quality audit report metrics.
        """
        return self._run_audit(source_id=None, sample_ratio=sample_ratio)

    def audit_dataset(self, dataset_id: str, sample_ratio: float = 1.0) -> QualityAuditReport:
        """
        Audits a specific dataset by source ID.
        """
        return self._run_audit(source_id=dataset_id, sample_ratio=sample_ratio)

    def _run_audit(self, source_id: Optional[str], sample_ratio: float) -> QualityAuditReport:
        discovered_partitions = self.registry.discover_partitions()
        if source_id:
            discovered_partitions = [p for p in discovered_partitions if p.source_id == source_id]

        total_audited = 0
        schema_compliant_count = 0
        validation_pass_count = 0
        malformed_count = 0

        seen_sample_ids: Set[str] = set()
        duplicate_sample_ids = 0

        seen_prompt_hashes: Set[str] = set()
        duplicate_prompt_hashes = 0

        missing_fields: Dict[str, int] = {
            "taxonomy_node": 0,
            "turns": 0,
            "evaluations": 0,
            "dataset_metadata": 0,
            "parser_metadata": 0,
            "validation": 0
        }

        missing_taxonomy_count = 0
        missing_evaluations_count = 0
        missing_validation_count = 0

        confidence_sum = 0.0
        confidence_cnt = 0

        evals_present_count = 0

        parser_versions: Dict[str, int] = {}
        dataset_versions: Dict[str, int] = {}

        # Clamp sample ratio between 0.001 and 1.0
        sample_ratio = max(0.001, min(1.0, sample_ratio))

        for part in discovered_partitions:
            for raw_dict in self.calculator.stream_records(part.partition_path):
                # Probabilistic sampling check
                if sample_ratio < 1.0 and random.random() > sample_ratio:
                    continue

                total_audited += 1

                # 1. Schema Validation Check
                try:
                    record = AttackRecord.model_validate(raw_dict)
                    schema_compliant_count += 1
                except Exception:
                    malformed_count += 1
                    continue

                # 2. Duplicate Sample ID Check
                sid = str(record.sample_id)
                if sid in seen_sample_ids:
                    duplicate_sample_ids += 1
                else:
                    seen_sample_ids.add(sid)

                # 3. Duplicate Prompt Semantic Hash Check
                prompt_content = ""
                for turn in record.turns:
                    for msg in turn.messages:
                        if msg.is_injection_source:
                            prompt_content += msg.content

                if prompt_content:
                    p_hash = hashlib.sha256(prompt_content.encode("utf-8")).hexdigest()
                    if p_hash in seen_prompt_hashes:
                        duplicate_prompt_hashes += 1
                    else:
                        seen_prompt_hashes.add(p_hash)

                # 4. Field Completeness Checks
                if not record.taxonomy_node or record.taxonomy_node == "unknown":
                    missing_fields["taxonomy_node"] += 1
                    missing_taxonomy_count += 1

                if not record.turns:
                    missing_fields["turns"] += 1

                if not record.evaluations:
                    missing_fields["evaluations"] += 1
                    missing_evaluations_count += 1
                else:
                    evals_present_count += 1

                val_res = record.validation
                if not val_res:
                    raw_vals = raw_dict.get("validation_results", [])
                    if isinstance(raw_vals, list) and len(raw_vals) > 0:
                        all_passed = True
                        for item in raw_vals:
                            if isinstance(item, dict):
                                if not item.get("is_valid", True):
                                    all_passed = False
                                confidence_sum += float(item.get("confidence", 1.0))
                                confidence_cnt += 1
                        if all_passed:
                            validation_pass_count += 1
                    else:
                        missing_fields["validation"] += 1
                        missing_validation_count += 1
                else:
                    if val_res.is_valid:
                        validation_pass_count += 1
                    confidence_sum += val_res.confidence
                    confidence_cnt += 1

                # 5. Metadata Distribution Tracking
                p_ver = record.parser_metadata.parser_version if record.parser_metadata else "unknown"
                parser_versions[p_ver] = parser_versions.get(p_ver, 0) + 1

                d_id = record.dataset_metadata.dataset_id if record.dataset_metadata else "unknown"
                dataset_versions[d_id] = dataset_versions.get(d_id, 0) + 1

        schema_pass_rate = round(schema_compliant_count / total_audited, 4) if total_audited > 0 else 0.0
        val_pass_rate = round(validation_pass_count / total_audited, 4) if total_audited > 0 else 0.0
        avg_confidence = round(confidence_sum / confidence_cnt, 4) if confidence_cnt > 0 else 0.0
        eval_completeness = round(evals_present_count / total_audited, 4) if total_audited > 0 else 0.0

        return QualityAuditReport(
            total_records_audited=total_audited,
            schema_compliance_rate=schema_pass_rate,
            validation_pass_rate=val_pass_rate,
            missing_field_counts=missing_fields,
            malformed_records=malformed_count,
            duplicate_sample_ids=duplicate_sample_ids,
            duplicate_semantic_hashes=duplicate_prompt_hashes,
            annotation_confidence_average=avg_confidence,
            evaluation_completeness=eval_completeness,
            parser_version_distribution=parser_versions,
            dataset_version_distribution=dataset_versions,
            records_with_missing_taxonomy=missing_taxonomy_count,
            records_with_missing_evaluations=missing_evaluations_count,
            records_with_missing_validation_metadata=missing_validation_count
        )
