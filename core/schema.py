from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID

class LicenseType(str, Enum):
    """Standardized license types for datasets."""
    MIT = "MIT"
    APACHE_2_0 = "Apache-2.0"
    CC_BY_4_0 = "CC-BY-4.0"
    CC_BY_NC_4_0 = "CC-BY-NC-4.0"
    PROPRIETARY = "Proprietary"
    OTHER = "Other"

class LicenseMetadata(BaseModel):
    """Metadata regarding the license of the dataset."""
    name: LicenseType = Field(description="Standardized license name.")
    url: Optional[str] = Field(None, description="Link to the license text.")

class ParserMetadata(BaseModel):
    """Lineage information about how the record was parsed, ensuring reproducibility."""
    parser_version: str = Field(description="Version of the parser plugin.")
    source_plugin: str = Field(description="Name of the plugin (e.g., 'hackaprompt').")
    raw_file_sha256: str = Field(description="SHA256 checksum of the source data file.")

class DatasetMetadata(BaseModel):
    """Metadata about the external dataset this record belongs to."""
    dataset_id: str = Field(description="Unique string identifier for the dataset.")
    description: Optional[str] = Field(None, description="Description of the dataset.")
    license: LicenseMetadata = Field(description="License information.")

class ValidationResult(BaseModel):
    """Result from automated or manual validation checks."""
    is_valid: bool = Field(description="Whether the record passed validation.")
    validator_name: str = Field(description="Name of the validator (e.g., 'JSON-Schema-Check').")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score from 0 to 1.")
    errors: List[str] = Field(default_factory=list, description="Validation errors if any.")

class EmbeddingReference(BaseModel):
    """Reference to dense embeddings stored outside the main record (e.g., Milvus/FAISS)."""
    model_name: str = Field(description="Embedding model used (e.g., 'mE5-large').")
    vector_id: str = Field(description="ID of the vector in the external vector database.")

class ArtifactType(str, Enum):
    """Supported multimodal artifact types."""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    CODE = "code"

class Artifact(BaseModel):
    """Multimodal artifacts attached to messages or attacks."""
    artifact_id: str = Field(description="Unique ID for this artifact.")
    artifact_type: ArtifactType = Field(description="Type of the artifact.")
    uri: str = Field(description="Local path or remote URL to the artifact.")
    sha256: str = Field(description="Checksum of the artifact file.")

class ToolCall(BaseModel):
    """A tool call invoked by the agent or simulated by the attacker."""
    tool_name: str = Field(description="Name of the tool.")
    arguments: Dict[str, Any] = Field(description="JSON arguments passed to the tool.")
    is_malicious: bool = Field(default=False, description="Flag indicating if the arguments contain an injected payload.")

class MessageRole(str, Enum):
    """Role of the message participant."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    ENVIRONMENT = "environment"

class Message(BaseModel):
    """A single message within a conversation turn."""
    role: MessageRole = Field(description="Role of the message sender.")
    content: str = Field(description="Text content of the message.")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="List of tool calls initiated in this message.")
    artifacts: List[Artifact] = Field(default_factory=list, description="Multimodal artifacts attached to this message.")
    is_injection_source: bool = Field(default=False, description="True if this message introduces the malicious payload.")

class ConversationTurn(BaseModel):
    """A single turn composed of messages (e.g., user trigger and agent response)."""
    turn_id: int = Field(ge=0, description="0-indexed turn number.")
    messages: List[Message] = Field(min_length=1, description="Messages within this turn.")

class EvaluationMetadata(BaseModel):
    """Metadata regarding evaluations performed on this attack record."""
    target_model: str = Field(description="The model the attack was tested against (e.g., 'gpt-4o').")
    attack_success: bool = Field(description="Whether the attack bypassed safety guardrails.")
    severity_score: float = Field(ge=0.0, le=10.0, description="Severity of the attack impact.")
    evaluator_model: str = Field(description="The judge model that performed the evaluation.")

class AttackRecord(BaseModel):
    """
    The root schema for an AegisSwarm attack sample.
    Supports JSON Schema generation natively via Pydantic.
    """
    model_config = ConfigDict(
        title="AegisSwarm Attack Record",
        populate_by_name=True,
        validate_assignment=True
    )
    
    sample_id: UUID = Field(description="UUIDv7 unique identifier for the attack sample.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp.")
    
    dataset_metadata: DatasetMetadata = Field(description="Origin dataset metadata.")
    parser_metadata: ParserMetadata = Field(description="Parser lineage information.")
    
    taxonomy_node: str = Field(description="Primary category from the AegisSwarm Attack Taxonomy.")
    difficulty_level: str = Field(description="Assessed difficulty level (e.g., Low, Medium, High, Expert).")
    
    turns: List[ConversationTurn] = Field(min_length=1, description="The multi-turn conversation trace of the attack.")
    
    evaluations: List[EvaluationMetadata] = Field(default_factory=list, description="Model evaluation results.")
    embeddings: List[EmbeddingReference] = Field(default_factory=list, description="Semantic embeddings.")
    validation: Optional[ValidationResult] = Field(None, description="Data quality validation status.")

    @field_validator("turns")
    @classmethod
    def validate_injection_source(cls, turns: List[ConversationTurn]) -> List[ConversationTurn]:
        """Ensure at least one message in the trace is flagged as the injection source."""
        has_injection = any(
            msg.is_injection_source
            for turn in turns
            for msg in turn.messages
        )
        if not has_injection:
            raise ValueError("An attack record must contain at least one message flagged as 'is_injection_source'.")
        return turns
