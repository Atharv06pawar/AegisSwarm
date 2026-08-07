# Contributing to AegisSwarm

Thank you for your interest in contributing to AegisSwarm! AegisSwarm is an open-source research initiative designed to unify AI attack datasets, autonomous red-teaming benchmarks, and Universal Attack Ontology (AUAO v1.0) representations across academic and industrial laboratories.

---

## 1. Development Setup

### Prerequisites
- **Python 3.10+** (Python 3.11/3.13 recommended)
- **Git**
- **Virtual Environment (`venv` or `uv`)**

### Quick Setup Steps

```bash
# 1. Clone the repository
git clone https://github.com/Atharv06pawar/AegisSwarm.git
cd AegisSwarm

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

# 3. Install core dependencies and development tools
pip install -r requirements.txt
pip install pytest pytest-cov ruff mypy
```

---

## 2. Coding Standards

AegisSwarm follows Microsoft Research and Google DeepMind software engineering standards:

- **Type Hints**: Strict typing is enforced using Pydantic v2 and Python typing module (`typing.Iterator`, `typing.Dict`, `typing.Optional`). Run `mypy` before submitting code.
- **Code Style**: Format code using `ruff format` or `black`. Line length limit is **100 characters**.
- **Docstrings**: All public classes, methods, and dataset plugins MUST contain Google-style or Sphinx docstrings explaining arguments, return types, and exceptions raised.
- **Memory Safety**: Never load entire datasets into memory. Use Python generators (`yield`) for streaming operations.

---

## 3. Plugin Development Guide

AegisSwarm relies on a plugin-centric streaming architecture. To add support for a new dataset benchmark (e.g. `my_dataset.py`):

1. **Subclass `BaseDatasetPlugin`**: Create `plugins/datasets/my_dataset.py`.
2. **Implement Required Contract Methods**:
   - `fetch() -> str`: Locates or streams raw data into `raw/my_dataset/`.
   - `parse(raw_data_path: str) -> Iterator[Dict[str, Any]]`: Yields raw line-by-line dictionaries.
   - `normalize(raw_record: Dict[str, Any]) -> AttackRecord`: Maps raw records to `core.schema.AttackRecord`.
   - `metadata() -> DatasetMetadata`: Returns dataset attribution, license, and ID.
   - `validate(records: Iterator[AttackRecord]) -> Iterator[AttackRecord]`: Filters corrupted records.
3. **Register Plugin Test**: Add an integration test in `tests/test_my_dataset_pipeline.py`.

See [`docs/PLUGIN_DEVELOPMENT.md`](docs/PLUGIN_DEVELOPMENT.md) for full developer instructions.

---

## 4. Branching and Commit Conventions

- **Branch Naming**:
  - Feature: `feat/add-garak-plugin`
  - Bugfix: `fix/schema-import-mismatch`
  - Documentation: `docs/update-auao-spec`
- **Commit Messages**: Use [Conventional Commits](https://www.conventionalcommits.org/):
  ```bash
  feat(plugins): implement agentdojo indirect injection plugin
  fix(storage): resolve atomic POSIX replace deadlock on Windows
  docs(auao): update section 5 mapping rules for PyRIT
  ```

---

## 5. Pull Request Process & Checklist

1. Open a feature branch from `main`.
2. Ensure all unit and integration tests pass:
   ```bash
   pytest tests/
   ```
3. Verify that your dataset plugin supports generator streaming and does not leak memory on large dataset samples.
4. Submit a Pull Request targeting `main` with a clear summary of changes.

---

## 6. Review Checklist

Before requesting review, ensure:
- [ ] Code passes `pytest` without failures.
- [ ] All new functions include Pydantic / typing hints.
- [ ] Plugin does not load complete file into RAM.
- [ ] AUAO Taxonomy mapping is registered in `ontology/ontology_mapping_rules.md`.
