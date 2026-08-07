# AegisSwarm Plugin Development Guide

**Target Audience**: AI Security Developers, Integration Engineers, Red Team Tool Authors  
**Prerequisites**: Python 3.10+, Pydantic v2, Generator Streaming Concepts  

---

## 1. Overview

AegisSwarm uses a **plugin-centric streaming architecture** to ingest external security datasets, benchmark traces, and red-teaming outputs. Every dataset integration is implemented as an independent plugin subclassing `core.plugin_base.BaseDatasetPlugin`.

Plugins MUST NOT perform storage, batching, orchestration, or CLI formatting. Their sole responsibility is to stream raw data, normalize raw dictionaries into `AttackRecord` objects, and filter corrupted entries.

---

## 2. Plugin Contract Reference

Your plugin must implement the following 5 methods and 2 properties:

```python
from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any
from core.schema import AttackRecord, DatasetMetadata

class BaseDatasetPlugin(ABC):
    @property
    @abstractmethod
    def dataset_id(self) -> str: ...

    @property
    @abstractmethod
    def parser_version(self) -> str: ...

    @abstractmethod
    def metadata(self) -> DatasetMetadata: ...

    @abstractmethod
    def fetch(self) -> str: ...

    @abstractmethod
    def parse(self, raw_data_path: str) -> Iterator[Dict[str, Any]]: ...

    @abstractmethod
    def normalize(self, raw_record: Dict[str, Any]) -> AttackRecord: ...

    def validate(self, records: Iterator[AttackRecord]) -> Iterator[AttackRecord]: ...
```

---

## 3. Step-by-Step Plugin Implementation

### Step 1: Create Plugin File
Create a new file in `plugins/datasets/<your_dataset>.py`.

```python
import json
import uuid
from pathlib import Path
from typing import Iterator, Dict, Any, List

from core.plugin_base import BaseDatasetPlugin
from core.schema import (
    AttackRecord, DatasetMetadata, ParserMetadata,
    LicenseMetadata, LicenseType, ConversationTurn, Message, MessageRole,
    EvaluationMetadata, ValidationResult
)

class MyDatasetPlugin(BaseDatasetPlugin):
    @property
    def dataset_id(self) -> str:
        return "my_dataset"

    @property
    def parser_version(self) -> str:
        return "1.0.0"

    def metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            dataset_id=self.dataset_id,
            description="My Custom Security Dataset.",
            license=LicenseMetadata(name=LicenseType.MIT, url="https://example.com")
        )

    def fetch(self) -> str:
        raw_dir = Path("raw/my_dataset")
        raw_dir.mkdir(parents=True, exist_ok=True)
        file_path = raw_dir / "dataset.jsonl"
        if not file_path.exists():
            # Download or write cached raw file
            pass
        return str(file_path)

    def parse(self, raw_data_path: str) -> Iterator[Dict[str, Any]]:
        with open(raw_data_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)

    def normalize(self, raw_record: Dict[str, Any]) -> AttackRecord:
        prompt = str(raw_record.get("prompt", ""))
        msg = Message(role=MessageRole.USER, content=prompt, is_injection_source=True)
        turn = ConversationTurn(turn_id=0, messages=[msg])

        return AttackRecord(
            sample_id=uuid.uuid4(),
            taxonomy_node="AUAO-PI-DIR-RO-AUTH-SYS",
            difficulty_level="Medium",
            turns=[turn],
            evaluations=[],
            dataset_metadata=self.metadata(),
            parser_metadata=ParserMetadata(
                parser_version=self.parser_version,
                source_plugin=self.dataset_id,
                raw_file_sha256="COMPUTED_BY_ORCHESTRATOR"
            )
        )

    def validate(self, records: Iterator[AttackRecord]) -> Iterator[AttackRecord]:
        for record in records:
            if record.turns and record.turns[0].messages[0].content.strip():
                yield record
```

---

## 4. Best Practices & Anti-Patterns

### ✅ Best Practices
- **Use Generators (`yield`)**: `parse()`, `normalize()`, and `validate()` MUST yield records iteratively.
- **Set `is_injection_source = True`**: Ensure at least one `Message` per record has `is_injection_source = True`.
- **Reference AUAO Taxonomy**: Map categories accurately using `ontology/ontology_mapping_rules.md`.

### ❌ Anti-Patterns
- **Loading Full Files into RAM (`json.load(f)`)**: Never load multi-gigabyte lists into RAM.
- **Handling Storage/Filesystem Writing inside Plugins**: Do not call `to_csv()` or `batch_write()` inside your plugin.
- **Ignoring Validation Errors**: Do not suppress invalid Pydantic objects silently without logging or filtering.

---

## 5. Plugin Registration & Testing

Plugins located in `plugins/datasets/` are auto-discovered by `PluginRegistry.discover()`.

Verify registration via CLI:
```bash
python main.py discover
```

Add an integration test in `tests/test_<your_dataset>_pipeline.py`:
```python
def test_plugin_pipeline():
    plugin = MyDatasetPlugin()
    path = plugin.fetch()
    records = list(plugin.validate(plugin.normalize(r) for r in plugin.parse(path)))
    assert len(records) > 0
```
