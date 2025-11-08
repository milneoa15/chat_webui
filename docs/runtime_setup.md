# ROCm Runtime Setup

This project assumes **one** ROCm-enabled llama.cpp runtime is available at a time. There are two supported paths:

1. Build llama.cpp locally with HIP/ROCm flags.
2. Copy the LM Studio “ROCm llama.cpp (Windows) v1.55.0” runtime pack that already ships with a prebuilt binary.

Both workflows share the same destination folder structure under `runtime/`.

```
runtime/
  lmstudio-rocm-1.55.0/
    bin/
    llama-server.exe
    ggml-rocm.dll
    runtime-pack.json  # metadata added by copy script
  custom-build/
    bin/
    llama.cpp artifacts...
```

## Prerequisites

- Windows 11 with the latest [ROCm for Windows preview drivers](https://www.amd.com/en/products/software/rocm) installed.
- Visual Studio Build Tools 2022 + C++ workload (for MSVC) or Ninja/Clang for alternative builds.
- `git`, `cmake`, and Python 3.11+ available on `$PATH`.
- Optional: [`uv`](https://docs.astral.sh/uv/) to run Python scripts without managing a venv manually.

## 1. Build llama.cpp with ROCm

The helper script lives at `infra/runtime/build_llamacpp_rocm.py`.

```powershell
uv run python infra/runtime/build_llamacpp_rocm.py `
  --ref master `
  --source-dir .runtime/llama.cpp `
  --build-dir .runtime/build-rocm `
  --generator "Ninja"
```

The script performs:

1. Clone or update `ggerganov/llama.cpp`.
2. Configure CMake with `LLAMA_HIPBLAS=1`, `LLAMA_CLBLAST=0`, `LLAMA_BUILD_SERVER=ON`, and related flags.
3. Invoke `cmake --build … --target llama`.

Artifacts are left under `.runtime/build-rocm/` so contributors can copy the produced binaries into `runtime/custom-build/` or elsewhere as needed.

### Python bindings

`llama-cpp-python` is an optional extra that wires the FastAPI runtime wrapper directly to a ROCm-enabled llama.cpp build. Install it only on machines that already have the right toolchain:

```powershell
uv sync --extra runtime
```

If the dependency fails to build (e.g., missing Visual Studio Build Tools), you can continue working on the backend via the mock runtime or LM Studio server integration. The FastAPI endpoints will raise a clear `RuntimeNotAvailableError` until the bindings become available.

### Notes

- Pass `--hip-path` if HIP is installed in a non-standard directory.
- Use `--target llama-server` to build the HTTP server binary instead of the CLI.
- Building on Windows still requires the AMD HIP SDK even though ROCm on Windows uses a compatibility layer.

## 2. Copy the LM Studio runtime pack

If you have LM Studio installed, locate the folder labeled **“ROCm llama.cpp (Windows) v1.55.0”** inside its runtime packs directory. Use the automation script to copy it into this repository with checksum validation:

```powershell
uv run python infra/runtime/copy_runtime_pack.py `
  "C:\Users\<you>\AppData\Local\Programs\LM Studio\runtime\ROCm llama.cpp (Windows) v1.55.0" `
  --expected-sha256 <value from LM Studio release notes> `
  --destination runtime/lmstudio-rocm-1.55.0
```

What the script does:

1. Computes a deterministic SHA-256 of all files in the source directory (or an archive).
2. Compares it against `--expected-sha256` if provided.
3. Copies the tree into `runtime/lmstudio-rocm-1.55.0`.
4. Writes `runtime-pack.json` with the version label + digest for future audits.

Re-run with `--force` to overwrite an existing install.

## Next Steps

After the runtime exists locally, export `CHATBOT_RUNTIME_PATH` (see `backend/app/config.py`) or update `.env` so the backend knows where to find binaries. Integration with the FastAPI runtime service and database-backed configuration is covered in Phase 2 of the implementation plan.
