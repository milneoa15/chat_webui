"""SQLModel ORM models."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from backend.app.utils.clock import utcnow


class InstalledModel(SQLModel, table=True):
    """GGUF artifact installed on disk."""

    __tablename__ = "installed_models"

    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(
        index=True,
        unique=True,
        description="Stable identifier derived from filename.",
    )
    display_name: str
    file_path: str = Field(description="Absolute path to the GGUF file.")
    quantization: str | None = None
    context_length: int | None = None
    parameter_count: float | None = None
    size_bytes: int | None = None
    checksum_sha256: str | None = Field(default=None, index=True)
    is_active: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
    last_loaded_at: datetime | None = None


class RuntimeConfig(SQLModel, table=True):
    """Default inference configuration applied when loading a model."""

    __tablename__ = "runtime_config"

    id: int | None = Field(default=1, primary_key=True)
    context_length: int = Field(default=4096, ge=256, description="Context window size.")
    gpu_layers: int | None = Field(
        default=None,
        ge=0,
        description="Number of layers offloaded to GPU.",
    )
    cpu_threads: int = Field(default=8, ge=1)
    eval_batch_size: int = Field(default=128, ge=1)
    kv_cache_placement: str = Field(default="auto", description="KV cache placement hint.")
    use_mmap: bool = Field(default=True, description="Pass --mmap flag.")
    keep_in_memory: bool = Field(default=True, description="Keep tensors resident between prompts.")
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
