"""Runtime + model lifecycle endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlmodel import Session, select

from backend.app.config import settings
from backend.app.db.models import InstalledModel, RuntimeConfig
from backend.app.db.session import get_session
from backend.app.runtime import get_runtime_manager
from backend.app.runtime.manager import LlamaRuntime, RuntimeNotAvailableError
from backend.app.schemas.runtime import (
    InstalledModelRead,
    MemoryStats,
    ModelListResponse,
    ModelSelectionRequest,
    ModelUploadResponse,
    RuntimeConfigResponse,
    RuntimeConfigSchema,
    RuntimeLoadRequest,
    RuntimeState,
)
from backend.app.utils.clock import utcnow
from backend.app.utils.file_ops import (
    infer_quantization_from_filename,
    save_upload,
    sha256_file,
    slugify,
)

router = APIRouter(prefix="/runtime", tags=["runtime"])


def _serialize_model(model: InstalledModel) -> InstalledModelRead:
    return InstalledModelRead.model_validate(model)


def _ensure_default_config(session: Session) -> RuntimeConfig:
    config = session.get(RuntimeConfig, 1)
    if not config:
        config = RuntimeConfig()
        session.add(config)
        session.commit()
        session.refresh(config)
    return config


def _config_to_schema(config: RuntimeConfig) -> RuntimeConfigSchema:
    return RuntimeConfigSchema(
        context_length=config.context_length,
        gpu_layers=config.gpu_layers,
        cpu_threads=config.cpu_threads,
        eval_batch_size=config.eval_batch_size,
        kv_cache_placement=config.kv_cache_placement,  # type: ignore[arg-type]
        use_mmap=config.use_mmap,
        keep_in_memory=config.keep_in_memory,
    )


def _apply_schema_to_config(config: RuntimeConfig, schema: RuntimeConfigSchema) -> RuntimeConfig:
    for field, value in schema.model_dump().items():
        setattr(config, field, value)
    config.updated_at = utcnow()
    return config


def _get_model(session: Session, model_id: int) -> InstalledModel:
    model = session.get(InstalledModel, model_id)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found.")
    return model


def _dedupe_slug(session: Session, base_slug: str) -> str:
    slug = base_slug
    counter = 2
    while session.exec(select(InstalledModel).where(InstalledModel.slug == slug)).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def _deactivate_all(session: Session) -> None:
    models = session.exec(select(InstalledModel).where(InstalledModel.is_active.is_(True))).all()
    for item in models:
        item.is_active = False
        item.updated_at = utcnow()


@router.get("/models", response_model=ModelListResponse)
def list_models(session: Session = Depends(get_session)) -> ModelListResponse:
    """Return installed GGUF artifacts."""
    models = session.exec(select(InstalledModel).order_by(InstalledModel.created_at.desc())).all()
    return ModelListResponse(models=[_serialize_model(model) for model in models])


@router.post(
    "/models/upload",
    response_model=ModelUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_model(
    file: UploadFile = File(...),
    display_name: str | None = Form(None),
    quantization: str | None = Form(None),
    context_length: int | None = Form(None),
    parameter_count: float | None = Form(None),
    session: Session = Depends(get_session),
) -> ModelUploadResponse:
    """Upload a GGUF file and register metadata."""
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required.")
    filename = Path(file.filename).name
    base_slug = slugify(Path(filename).stem)
    slug = _dedupe_slug(session, base_slug)
    destination = settings.models_dir / f"{slug}{Path(filename).suffix}"
    bytes_written = await save_upload(file, destination)
    digest = sha256_file(destination)
    model = InstalledModel(
        slug=slug,
        display_name=display_name or Path(filename).stem,
        file_path=str(destination),
        quantization=quantization or infer_quantization_from_filename(filename),
        context_length=context_length,
        parameter_count=parameter_count,
        size_bytes=bytes_written,
        checksum_sha256=digest,
    )
    session.add(model)
    session.commit()
    session.refresh(model)
    return ModelUploadResponse(model=_serialize_model(model))


@router.post("/models/select", response_model=ModelUploadResponse)
def select_model(
    payload: ModelSelectionRequest,
    session: Session = Depends(get_session),
) -> ModelUploadResponse:
    """Mark a model as active (does not load it into memory)."""
    model = _get_model(session, payload.model_id)
    _deactivate_all(session)
    model.is_active = True
    model.updated_at = utcnow()
    session.add(model)
    session.commit()
    session.refresh(model)
    return ModelUploadResponse(model=_serialize_model(model))


@router.get("/config", response_model=RuntimeConfigResponse)
def get_runtime_config(session: Session = Depends(get_session)) -> RuntimeConfigResponse:
    config = _ensure_default_config(session)
    return RuntimeConfigResponse(config=_config_to_schema(config))


@router.put("/config", response_model=RuntimeConfigResponse)
def update_runtime_config(
    payload: RuntimeConfigSchema,
    session: Session = Depends(get_session),
) -> RuntimeConfigResponse:
    config = _ensure_default_config(session)
    config = _apply_schema_to_config(config, payload)
    session.add(config)
    session.commit()
    session.refresh(config)
    return RuntimeConfigResponse(config=_config_to_schema(config))


@router.get("/state", response_model=RuntimeState)
def runtime_state(
    session: Session = Depends(get_session),
    runtime: LlamaRuntime = Depends(get_runtime_manager),
) -> RuntimeState:
    state = runtime.get_state()
    if not state:
        return RuntimeState(loaded=False)
    model = _get_model(session, state.model_id)
    return RuntimeState(
        loaded=True,
        model=_serialize_model(model),
        config=state.config,
        runtime_path=str(Path(model.file_path).parent),
        loaded_at=state.loaded_at,
    )


@router.post("/load", response_model=RuntimeState)
def load_model(
    payload: RuntimeLoadRequest,
    session: Session = Depends(get_session),
    runtime: LlamaRuntime = Depends(get_runtime_manager),
) -> RuntimeState:
    model = _get_model(session, payload.model_id)
    config_model = _ensure_default_config(session)
    config_schema = payload.config_override or _config_to_schema(config_model)

    try:
        state = runtime.load_model(
            model_id=model.id,  # type: ignore[arg-type]
            model_path=Path(model.file_path),
            config=config_schema,
        )
    except RuntimeNotAvailableError as exc:  # pragma: no cover - depends on optional install
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    _deactivate_all(session)
    model.is_active = True
    model.last_loaded_at = state.loaded_at
    model.updated_at = utcnow()
    session.add(model)
    session.commit()
    session.refresh(model)

    return RuntimeState(
        loaded=True,
        model=_serialize_model(model),
        config=config_schema,
        runtime_path=str(Path(model.file_path).parent),
        loaded_at=state.loaded_at,
    )


@router.post("/unload", response_model=RuntimeState)
def unload_model(
    session: Session = Depends(get_session),
    runtime: LlamaRuntime = Depends(get_runtime_manager),
) -> RuntimeState:
    runtime.unload_model()
    _deactivate_all(session)
    session.commit()
    return RuntimeState(loaded=False)


@router.get("/memory", response_model=MemoryStats)
def runtime_memory(runtime: LlamaRuntime = Depends(get_runtime_manager)) -> MemoryStats:
    snapshot = runtime.memory_snapshot()
    return MemoryStats(
        resident_bytes=snapshot.resident_bytes,
        vram_bytes=snapshot.vram_bytes,
        source=snapshot.source,
    )
