"""Schemas for runtime + model lifecycle APIs."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class KVCachePlacement(str, Enum):
    """Where the KV cache should reside."""

    AUTO = "auto"
    CPU = "cpu"
    GPU = "gpu"
    HYBRID = "hybrid"


class RuntimeConfigSchema(BaseModel):
    """Inference configuration shared across models."""

    context_length: int = Field(4096, ge=256, le=32768)
    gpu_layers: int | None = Field(
        default=None,
        ge=0,
        description="Number of transformer layers to place on the GPU.",
    )
    cpu_threads: int = Field(8, ge=1, le=128)
    eval_batch_size: int = Field(128, ge=1, le=4096)
    kv_cache_placement: KVCachePlacement = KVCachePlacement.AUTO
    use_mmap: bool = True
    keep_in_memory: bool = True


class InstalledModelRead(BaseModel):
    """Serialized InstalledModel row."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    display_name: str
    file_path: str
    quantization: str | None
    context_length: int | None
    parameter_count: float | None
    size_bytes: int | None
    checksum_sha256: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_loaded_at: datetime | None


class ModelListResponse(BaseModel):
    models: list[InstalledModelRead]


class ModelSelectionRequest(BaseModel):
    model_id: int


class RuntimeLoadRequest(ModelSelectionRequest):
    config_override: RuntimeConfigSchema | None = None


class RuntimeState(BaseModel):
    loaded: bool = False
    model: InstalledModelRead | None = None
    config: RuntimeConfigSchema | None = None
    runtime_path: str | None = None
    loaded_at: datetime | None = None


class MemoryStats(BaseModel):
    resident_bytes: int
    vram_bytes: int | None = Field(
        default=None,
        description="May be None if ROCm metrics unavailable.",
    )
    source: str


class RuntimeConfigResponse(BaseModel):
    config: RuntimeConfigSchema


class ModelUploadResponse(BaseModel):
    model: InstalledModelRead
