"""Runtime container factory."""

from backend.app.runtime.manager import LlamaRuntime

runtime_manager = LlamaRuntime()


def get_runtime_manager() -> LlamaRuntime:
    """Return the singleton runtime manager."""
    return runtime_manager
