# AegisSwarm Ingestion Pipeline Architecture

## 1. Pipeline Overview

The **AegisSwarm Ingestion Pipeline** (`aegis_ingest`) is a high-throughput, highly scalable Python-based ETL (Extract, Transform, Load) system. It is designed to autonomously fetch, parse, normalize, and enrich heterogeneous AI security datasets into the unified AegisSwarm JSON Schema.

## 2. UML Architecture Diagram

```mermaid
graph TD
    %% External Sources
    subgraph Sources ["External Data Sources"]
        GitHub[GitHub Repositories]
        HF[HuggingFace Datasets]
        Kaggle[Kaggle Datasets]
        Web[Web/Raw Files]
    end

    %% Stage 1: Discovery
    subgraph Stage1 ["1. Discovery & Ingestion"]
        Fetcher[Source Fetcher & Crawler]
        Registry[Dataset Registry DB]
        Fetcher --> Registry
    end
    Sources --> Fetcher

    %% Stage 2: Validation
    subgraph Stage2 ["2. Validation"]
        TypeCheck[MIME/Format Detection]
        Integrity[SHA256 Checksum]
    end
    Registry --> TypeCheck
    TypeCheck --> Integrity

    %% Stage 3: Parsing
    subgraph Stage3 ["3. Parsing"]
        ParseJSON[JSON / JSONL Parser]
        ParseCSV[CSV Parser]
        ParseText[YAML / Markdown / HTML / XML]
        ParsePDF[PDF / OCR Parser]
        
        Router{Format Router}
        Router -->|JSON| ParseJSON
        Router -->|CSV| ParseCSV
        Router -->|Text| ParseText
        Router -->|PDF| ParsePDF
    end
    Integrity --> Router

    %% Stage 4: Normalization
    subgraph Stage4 ["4. Normalization"]
        MapSchema[Schema Mapper]
        ValidateSchema[Draft 2020-12 Validator]
    end
    ParseJSON --> MapSchema
    ParseCSV --> MapSchema
    ParseText --> MapSchema
    ParsePDF --> MapSchema
    MapSchema --> ValidateSchema

    %% Stage 5 & 6: Deduplication & Semantic Clustering
    subgraph Stage5_6 ["5 & 6. Processing & Clustering"]
        Embedder[Text Embedding Vectorizer]
        LSH[MinHash/LSH Exact & Near-Exact Dedup]
        HDBSCAN[HDBSCAN Semantic Clustering]
    end
    ValidateSchema --> Embedder
    Embedder --> LSH
    LSH --> HDBSCAN

    %% Stage 7: Annotation
    subgraph Stage7 ["7. Auto-Annotation"]
        Heuristics[Regex/Heuristics Tagger]
        LLMJudge[LLM-as-a-Judge Tagger]
    end
    HDBSCAN --> Heuristics
    Heuristics --> LLMJudge

    %% Stage 8 & 9: Versioning & Output
    subgraph Stage8_9 ["8 & 9. Output & Versioning"]
        DVC[DVC / Delta Lake Versioning]
        Export[Parquet & JSONL Exporter]
    end
    LLMJudge --> DVC
    DVC --> Export
```

## 3. Python Project Structure

```text
aegis_ingest/
├── pyproject.toml                 # Poetry/Pipenv dependencies
├── main.py                        # CLI entry point (e.g., typer/click CLI)
├── config/
│   ├── __init__.py
│   ├── settings.py                # Pydantic BaseSettings (API keys, DB URIs)
│   └── dataset_registry.yaml      # Configuration of target datasets & fetch schedules
├── discovery/
│   ├── __init__.py
│   ├── fetcher_github.py          # GitHub API integration (clone, sparse-checkout)
│   ├── fetcher_huggingface.py     # `datasets` library integration
│   ├── fetcher_kaggle.py          # Kaggle API integration
│   └── fetcher_raw.py             # Basic HTTP/FTP downloaders
├── validation/
│   ├── __init__.py
│   ├── checksum.py                # SHA256 integrity validation
│   └── type_detector.py           # MIME sniffing and extension verification
├── parsers/
│   ├── __init__.py
│   ├── base_parser.py             # Abstract Base Class for all parsers
│   ├── json_parser.py             # Pandas/Polars JSON/JSONL handling
│   ├── tabular_parser.py          # CSV/Excel parsing
│   ├── markup_parser.py           # BeautifulSoup HTML, Markdown, XML parsing
│   ├── yaml_parser.py             # PyYAML parsing
│   └── pdf_parser.py              # PyPDF2, pdfplumber, and Tesseract OCR integration
├── normalizers/
│   ├── __init__.py
│   ├── schema_mapper.py           # Translates generic dicts into AegisSwarm objects
│   ├── pydantic_models.py         # Pydantic models for the AegisSwarm JSON Schema
│   └── mapping_rules/             # Dataset-specific mapping logic (e.g., JailbreakBench -> Aegis)
├── processing/
│   ├── __init__.py
│   ├── deduplication.py           # Locality-Sensitive Hashing (MinHash) via datasketch
│   ├── clustering.py              # Embedding generation (SentenceTransformers) & HDBSCAN
│   └── annotation.py              # LLM API calls (OpenAI/Anthropic) to backfill missing metadata
├── storage/
│   ├── __init__.py
│   ├── version_control.py         # Data Version Control (DVC) or Delta Lake bindings
│   └── export.py                  # PyArrow integration for writing Parquet/JSONL output
└── utils/
    ├── logger.py                  # Structured JSON logging
    └── concurrency.py             # Asyncio / multiprocessing executors
```

## 4. Reusable Modules & Libraries Recommendation

- **Core Data Processing**: `polars` (for fast, multi-threaded in-memory tabular operations) and `pyarrow` (for Parquet I/O).
- **Validation & Schema**: `pydantic` (for robust typing and schema mapping) and `jsonschema` (for raw JSON validation).
- **Parsing**: `beautifulsoup4` (HTML/XML), `pdfplumber` (PDFs text extraction), `pytesseract` (OCR fallback).
- **Embeddings & NLP**: `sentence-transformers` (for generating embeddings rapidly locally) and `spacy`.
- **Clustering & Dedup**: `datasketch` (for MinHash/LSH exact and near-deduplication of massive text corpora), `scikit-learn`, and `hdbscan` (for semantic attack clustering).
- **Pipeline Orchestration**: `prefect` or `dagster` (to schedule runs, track stage failures, and manage retries) instead of just raw scripts.
- **Versioning**: `dvc` (Data Version Control) integrated via CLI or python API to track changes per pipeline run.
