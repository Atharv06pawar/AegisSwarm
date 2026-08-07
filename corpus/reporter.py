import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from corpus.registry import CorpusRegistry
from corpus.statistics import CorpusStatisticsCalculator
from corpus.coverage import OntologyCoverageAnalyzer
from corpus.quality import CorpusQualityAuditor
from corpus.verifier import CorpusIntegrityVerifier

class CorpusReporter:
    """
    Publication-grade reporting engine for the AegisSwarm Corpus Management Subsystem.
    Combines analytics from CorpusRegistry, CorpusStatisticsCalculator, OntologyCoverageAnalyzer,
    CorpusQualityAuditor, and CorpusIntegrityVerifier into structured JSON reports and
    GitHub-Flavored Markdown research whitepapers.
    """

    def __init__(
        self,
        registry: Optional[CorpusRegistry] = None,
        calculator: Optional[CorpusStatisticsCalculator] = None,
        analyzer: Optional[OntologyCoverageAnalyzer] = None,
        auditor: Optional[CorpusQualityAuditor] = None,
        verifier: Optional[CorpusIntegrityVerifier] = None
    ):
        self.registry = registry or CorpusRegistry()
        self.calculator = calculator or CorpusStatisticsCalculator(registry=self.registry)
        self.analyzer = analyzer or OntologyCoverageAnalyzer(registry=self.registry, calculator=self.calculator)
        self.auditor = auditor or CorpusQualityAuditor(registry=self.registry, calculator=self.calculator)
        self.verifier = verifier or CorpusIntegrityVerifier(registry=self.registry)

    def generate_json(self) -> Dict[str, Any]:
        """
        Generates a comprehensive JSON dictionary containing all subsystem metrics.
        
        Returns:
            Dict[str, Any]: Complete serialized report object.
        """
        summary = self.registry.get_summary()
        datasets = self.registry.list_datasets()
        stats = self.calculator.compute_statistics()
        coverage = self.analyzer.analyze()
        quality = self.auditor.audit(sample_ratio=1.0)
        verification = self.verifier.verify()

        timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "generation_timestamp": timestamp,
            "corpus_summary": summary.model_dump(mode="json"),
            "datasets": [ds.model_dump(mode="json") for ds in datasets],
            "statistics": stats.model_dump(mode="json"),
            "coverage": coverage.model_dump(mode="json"),
            "quality": quality.model_dump(mode="json"),
            "verification": verification.model_dump(mode="json")
        }

    def generate_markdown(self) -> str:
        """
        Generates a publication-grade GitHub-Flavored Markdown research whitepaper.
        
        Returns:
            str: Markdown string content.
        """
        data = self.generate_json()
        ts = data["generation_timestamp"]
        summary = data["corpus_summary"]
        datasets = data["datasets"]
        stats = data["statistics"]
        cov = data["coverage"]
        qual = data["quality"]
        ver = data["verification"]

        md = []
        md.append("# AegisSwarm Universal AI Attack Corpus Research Whitepaper")
        md.append("")
        md.append(f"**Generated UTC Timestamp**: `{ts}`  ")
        md.append(f"**Ontology Framework**: `AegisSwarm Universal Attack Ontology (AUAO v1.0)`  ")
        md.append(f"**Data Lake Status**: `{ver['overall_status']}`")
        md.append("")
        md.append("---")
        md.append("")

        # 1. Executive Summary
        md.append("## 1. Executive Summary")
        md.append("")
        md.append(
            f"This publication report presents the authoritative status of the **AegisSwarm AI Attack Corpus**. "
            f"The corpus currently unifies **{summary['total_datasets']} benchmark datasets** comprising "
            f"**{stats['total_records']:,} AttackRecord entries** across **{stats['total_turns']:,} conversation turns** "
            f"and **{stats['total_messages']:,} messages**. Physical data lake storage footprint spans "
            f"**{summary['total_size_bytes'] / (1024*1024):.2f} MB** across **{summary['total_partitions']} partition files**."
        )
        md.append("")

        # 2. Corpus Overview
        md.append("## 2. Corpus Overview")
        md.append("")
        md.append("| Metric | Value |")
        md.append("| :--- | :--- |")
        md.append(f"| **Total Datasets** | {summary['total_datasets']} |")
        md.append(f"| **Total Partitions** | {summary['total_partitions']} |")
        md.append(f"| **Total Records** | {stats['total_records']:,} |")
        md.append(f"| **Total Turns** | {stats['total_turns']:,} |")
        md.append(f"| **Total Messages** | {stats['total_messages']:,} |")
        md.append(f"| **Storage Size** | {summary['total_size_bytes'] / (1024*1024):.2f} MB |")
        md.append(f"| **Data Lake Health** | `{ver['overall_status']}` ({ver['verification_percentage']}%) |")
        md.append("")

        # 3. Dataset Inventory
        md.append("## 3. Dataset Inventory")
        md.append("")
        md.append("| Dataset ID | Partitions | Formats | Total Size (Bytes) |")
        md.append("| :--- | :---: | :--- | :--- |")
        if datasets:
            for ds in datasets:
                fmts = ", ".join(ds["formats"]) if ds["formats"] else "N/A"
                md.append(f"| `{ds['source_id']}` | {ds['partition_count']} | {fmts} | {ds['total_size_bytes']:,} |")
        else:
            md.append("| *No datasets registered* | - | - | - |")
        md.append("")

        # 4. Statistics
        md.append("## 4. Corpus Statistics")
        md.append("")
        md.append(f"- **Average Turns per Record**: `{stats['average_turns_per_record']}`")
        md.append(f"- **Average Messages per Record**: `{stats['average_messages_per_record']}`")
        md.append(f"- **Average Injection Prompt Length**: `{stats['average_prompt_length']}` characters")
        md.append(f"- **Maximum Prompt Length**: `{stats['maximum_prompt_length']}` characters")
        md.append(f"- **Minimum Prompt Length**: `{stats['minimum_prompt_length']}` characters")
        md.append(f"- **Overall Evaluation Success Rate**: `{stats['evaluation_success_rate'] * 100:.2f}%`")
        md.append(f"- **Average Severity Score**: `{stats['average_severity_score']} / 10.0`")
        md.append("")

        # 5. Coverage Analysis
        md.append("## 5. AUAO v1.0 Coverage Analysis")
        md.append("")
        md.append(f"- **Total Taxonomy Nodes**: `{cov['total_taxonomy_nodes']}`")
        md.append(f"- **Represented Taxonomy Nodes**: `{cov['covered_taxonomy_nodes_count']}`")
        md.append(f"- **Coverage Percentage**: `{cov['coverage_percentage']}%`")
        md.append("")
        md.append("### Root Class Representation (`AUAO-RC-*`)")
        md.append("")
        md.append("| Root Domain ID | Record Count | Representation |")
        md.append("| :--- | :--- | :--- |")
        for rc_id, count in cov["root_class_coverage"].items():
            status_str = "✅ Covered" if count > 0 else "❌ Uncovered"
            md.append(f"| `{rc_id}` | {count:,} | {status_str} |")
        md.append("")

        # 6. Quality Metrics
        md.append("## 6. Quality Metrics Audit")
        md.append("")
        md.append(f"- **Audited Records**: `{qual['total_records_audited']:,}`")
        md.append(f"- **Schema Compliance Rate**: `{qual['schema_compliance_rate'] * 100:.2f}%`")
        md.append(f"- **Validation Pass Rate**: `{qual['validation_pass_rate'] * 100:.2f}%`")
        md.append(f"- **Annotation Confidence Average**: `{qual['annotation_confidence_average']}`")
        md.append(f"- **Evaluation Completeness**: `{qual['evaluation_completeness'] * 100:.2f}%`")
        md.append(f"- **Duplicate Sample IDs**: `{qual['duplicate_sample_ids']}`")
        md.append(f"- **Duplicate Semantic Hashes**: `{qual['duplicate_semantic_hashes']}`")
        md.append("")

        # 7. Verification Status
        md.append("## 7. Data Lake Cryptographic Verification Status")
        md.append("")
        md.append(f"- **Overall Status**: `{ver['overall_status']}`")
        md.append(f"- **Total Partitions Scanned**: `{ver['total_partitions_scanned']}`")
        md.append(f"- **Verified Files**: `{ver['verified_files']}`")
        md.append(f"- **Missing Files**: `{len(ver['missing_files'])}`")
        md.append(f"- **Corrupted Files**: `{len(ver['corrupted_files'])}`")
        md.append(f"- **Modified Files**: `{len(ver['modified_files'])}`")
        md.append(f"- **Verification Percentage**: `{ver['verification_percentage']}%`")
        md.append("")

        # 8. Target Models
        md.append("## 8. Target Models Evaluated")
        md.append("")
        if stats["unique_target_models"]:
            for tm in stats["unique_target_models"]:
                md.append(f"- `{tm}`")
        else:
            md.append("*No evaluation target models recorded*")
        md.append("")

        # 9. Taxonomy Distribution
        md.append("## 9. Taxonomy Distribution")
        md.append("")
        md.append("| AUAO Taxonomy Node | Record Count |")
        md.append("| :--- | :--- |")
        if stats["taxonomy_distribution"]:
            for t_node, t_cnt in stats["taxonomy_distribution"].items():
                md.append(f"| `{t_node}` | {t_cnt:,} |")
        else:
            md.append("| *No taxonomy distribution available* | - |")
        md.append("")

        # 10. Recommendations & Future Work
        md.append("## 10. Recommendations & Future Work")
        md.append("")
        md.append("1. **Expand Taxonomy Coverage**: Ingest additional datasets (WildTeaming, TensorTrust, PoisonedRAG) to cover unrepresented leaf nodes.")
        md.append("2. **Multimodal Payload Ingestion**: Increase dataset coverage for visual steganography and audio injection vectors (`AUAO-RC-10`).")
        md.append("3. **Distributed Ingestion Engine**: Scale chunked streaming ingestion using Ray worker nodes for multi-terabyte benchmarking.")
        md.append("")
        md.append("---")
        md.append("*AegisSwarm Corpus Reporter — Publication Standard RFC 2026*")

        return "\n".join(md)

    def export(self, output_dir: str = "outputs") -> Dict[str, str]:
        """
        Exports both corpus_report.md and corpus_report.json to the output directory.
        
        Args:
            output_dir (str): Destination directory path (default 'outputs').
            
        Returns:
            Dict[str, str]: Paths to written markdown and json files.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        json_data = self.generate_json()
        json_file = out_path / "corpus_report.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        md_content = self.generate_markdown()
        md_file = out_path / "corpus_report.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        return {
            "json": str(json_file.resolve()),
            "markdown": str(md_file.resolve())
        }
