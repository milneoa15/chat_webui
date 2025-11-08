"""Tests covering runtime + model lifecycle endpoints."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.config import settings
from backend.app.db.session import configure_engine, init_db
from backend.app.main import create_app
from backend.app.runtime import get_runtime_manager
from backend.app.runtime.manager import LoadedModelState, MemorySnapshot
from backend.app.utils.clock import utcnow


class FakeRuntime:
    """In-memory stand-in for llama.cpp bindings."""

    def __init__(self) -> None:
        self.state: LoadedModelState | None = None
        self.snapshot = MemorySnapshot(resident_bytes=42, vram_bytes=84, source="fake")

    def load_model(self, *, model_id: int, model_path: Path, config) -> LoadedModelState:
        self.state = LoadedModelState(
            model_id=model_id,
            model_path=model_path,
            config=config,
            loaded_at=utcnow(),
        )
        return self.state

    def unload_model(self) -> None:
        self.state = None

    def get_state(self) -> LoadedModelState | None:
        return self.state

    def memory_snapshot(self) -> MemorySnapshot:
        return self.snapshot


@pytest.fixture
def runtime_client(tmp_path, monkeypatch) -> Generator[tuple[TestClient, FakeRuntime], None, None]:
    """Create an isolated TestClient with a stub runtime + temp database."""
    original_db_url = settings.database_url
    data_dir = tmp_path / "state"
    models_dir = data_dir / "models"
    runtime_root = tmp_path / "runtime"
    db_path = data_dir / "runtime.db"

    monkeypatch.setattr(settings, "data_dir", data_dir, raising=False)
    monkeypatch.setattr(settings, "models_dir", models_dir, raising=False)
    monkeypatch.setattr(settings, "runtime_root", runtime_root, raising=False)
    monkeypatch.setattr(
        settings,
        "preferred_runtime_path",
        runtime_root / "lmstudio-rocm-1.55.0",
        raising=False,
    )
    monkeypatch.setattr(settings, "database_path", db_path, raising=False)
    monkeypatch.setattr(settings, "database_url", f"sqlite:///{db_path}", raising=False)
    settings.ensure_directories()

    configure_engine(settings.database_url)
    init_db()

    app = create_app()
    fake_runtime = FakeRuntime()
    app.dependency_overrides[get_runtime_manager] = lambda: fake_runtime

    try:
        with TestClient(app) as client:
            yield client, fake_runtime
    finally:
        app.dependency_overrides.pop(get_runtime_manager, None)
        configure_engine(original_db_url)


def test_model_upload_and_listing(runtime_client) -> None:
    client, _ = runtime_client
    response = client.post(
        "/api/runtime/models/upload",
        files={"file": ("tiny.gguf", b"GGUFTEST", "application/octet-stream")},
        data={"display_name": "Tiny", "quantization": "Q4_K_M"},
    )
    payload = response.json()

    assert response.status_code == 201
    assert payload["model"]["display_name"] == "Tiny"

    list_response = client.get("/api/runtime/models")
    assert list_response.status_code == 200
    models = list_response.json()["models"]
    assert len(models) == 1
    assert models[0]["slug"].startswith("tiny")


def test_model_select_load_and_state(runtime_client) -> None:
    client, runtime = runtime_client
    response = client.post(
        "/api/runtime/models/upload",
        files={"file": ("story.gguf", b"GGUF-2", "application/octet-stream")},
    )
    model_id = response.json()["model"]["id"]

    select_response = client.post("/api/runtime/models/select", json={"model_id": model_id})
    assert select_response.status_code == 200
    assert select_response.json()["model"]["is_active"] is True

    load_response = client.post("/api/runtime/load", json={"model_id": model_id})
    assert load_response.status_code == 200
    assert runtime.get_state() is not None

    state_response = client.get("/api/runtime/state")
    assert state_response.status_code == 200
    assert state_response.json()["loaded"] is True
    assert state_response.json()["model"]["id"] == model_id

    unload_response = client.post("/api/runtime/unload")
    assert unload_response.status_code == 200
    assert unload_response.json()["loaded"] is False
    assert runtime.get_state() is None


def test_runtime_config_and_memory(runtime_client) -> None:
    client, runtime = runtime_client
    config_response = client.get("/api/runtime/config")
    assert config_response.status_code == 200
    default_ctx = config_response.json()["config"]["context_length"]
    assert default_ctx == 4096

    update_payload = {
        "context_length": 8192,
        "gpu_layers": 24,
        "cpu_threads": 6,
        "eval_batch_size": 64,
        "kv_cache_placement": "gpu",
        "use_mmap": False,
        "keep_in_memory": False,
    }
    update_response = client.put("/api/runtime/config", json=update_payload)
    assert update_response.status_code == 200
    assert update_response.json()["config"]["context_length"] == 8192

    memory_response = client.get("/api/runtime/memory")
    assert memory_response.status_code == 200
    assert memory_response.json() == {
        "resident_bytes": runtime.snapshot.resident_bytes,
        "vram_bytes": runtime.snapshot.vram_bytes,
        "source": runtime.snapshot.source,
    }
