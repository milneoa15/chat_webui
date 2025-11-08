"""Runtime manager wrapping llama.cpp bindings."""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

import psutil

from backend.app.schemas.runtime import RuntimeConfigSchema
from backend.app.utils.clock import utcnow

try:
    from llama_cpp import Llama
except ImportError as exc:  # pragma: no cover
    Llama = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


@dataclass
class LoadedModelState:
    model_id: int
    model_path: Path
    config: RuntimeConfigSchema
    loaded_at: datetime


@dataclass
class MemorySnapshot:
    resident_bytes: int
    vram_bytes: int | None
    source: str


class RuntimeNotAvailableError(RuntimeError):
    """Raised when llama.cpp bindings are missing."""


class LlamaRuntime:
    """Thin wrapper around llama_cpp.Llama that enforces a single loaded model."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._llama: Llama | None = None
        self._state: LoadedModelState | None = None

    def load_model(
        self,
        *,
        model_id: int,
        model_path: Path,
        config: RuntimeConfigSchema,
    ) -> LoadedModelState:
        """Load a GGUF file into memory."""
        if Llama is None:
            raise RuntimeNotAvailableError(
                "llama-cpp-python is not available. "
                "Install extras or ensure the ROCm build succeeded."
            ) from _IMPORT_ERROR

        if not model_path.exists():
            raise FileNotFoundError(f"Model path {model_path} does not exist.")

        with self._lock:
            self._unload_locked()
            llama_args: dict[str, Any] = {
                "model_path": str(model_path),
                "n_ctx": config.context_length,
                "n_threads": config.cpu_threads,
                "n_batch": config.eval_batch_size,
                "use_mmap": config.use_mmap,
                "keep_in_memory": config.keep_in_memory,
            }
            if config.gpu_layers is not None:
                llama_args["n_gpu_layers"] = config.gpu_layers

            self._llama = Llama(**llama_args)
            state = LoadedModelState(
                model_id=model_id,
                model_path=model_path,
                config=config,
                loaded_at=utcnow(),
            )
            self._state = state
            return state

    def unload_model(self) -> None:
        """Release the currently loaded model."""
        with self._lock:
            self._unload_locked()

    def _unload_locked(self) -> None:
        self._llama = None
        self._state = None

    def get_state(self) -> LoadedModelState | None:
        """Return details about the loaded model, if any."""
        with self._lock:
            return self._state

    def memory_snapshot(self) -> MemorySnapshot:
        """Return host + GPU memory usage."""
        process = psutil.Process()
        rss = int(process.memory_info().rss)
        vram_bytes, source = self._read_rocm_vram_usage()
        return MemorySnapshot(resident_bytes=rss, vram_bytes=vram_bytes, source=source)

    @staticmethod
    def _read_rocm_vram_usage() -> tuple[int | None, str]:
        executable = shutil.which("rocm-smi") or shutil.which("rocm-smi.exe")
        if not executable:
            return None, "psutil"

        try:
            result = subprocess.run(
                [executable, "--showmeminfo", "vram"],
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError:
            return None, "psutil"

        if result.returncode != 0:
            return None, "psutil"

        match = re.search(r"Used VRAM.*?:\s*(\d+)\s*MB", result.stdout)
        if match:
            return int(match.group(1)) * 1024 * 1024, "rocm-smi"
        return None, "psutil"
