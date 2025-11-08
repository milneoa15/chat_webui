"""Invoke tasks for local automation."""

from invoke import task

def _frontend(ctx, command: str) -> None:
    ctx.run(f"cd frontend && {command}", echo=True, pty=True)


@task
def lint_backend(ctx) -> None:
    """Run ruff and black in check mode."""
    ctx.run("uv run ruff check backend", echo=True, pty=True)
    ctx.run("uv run black --check backend", echo=True, pty=True)


@task
def test_backend(ctx) -> None:
    """Execute backend pytest suite."""
    ctx.run("uv run pytest", echo=True, pty=True)


@task
def lint_frontend(ctx) -> None:
    """Run the frontend lint command."""
    _frontend(ctx, "npm run lint")


@task(
    help={
        "ref": "Git ref/tag for llama.cpp (default: master)",
        "generator": "Optional CMake generator such as Ninja",
        "hip_path": "Override HIP install path",
        "target": "CMake target name (llama, llama-server, etc.)",
    },
)
def build_rocm_runtime(ctx, ref="master", generator=None, hip_path=None, target="llama") -> None:
    """Wrapper around the ROCm llama.cpp build helper."""
    cmd = [
        "uv",
        "run",
        "python",
        "infra/runtime/build_llamacpp_rocm.py",
        f"--ref {ref}",
    ]
    if generator:
        cmd.extend(["--generator", f'"{generator}"'])
    if hip_path:
        cmd.extend(["--hip-path", f'"{hip_path}"'])
    if target and target != "llama":
        cmd.extend(["--target", target])
    ctx.run(" ".join(cmd), echo=True, pty=True)


@task(
    help={
        "source": "Path to LM Studio runtime directory/archive",
        "expected_sha256": "Hash published by LM Studio (optional but recommended)",
        "destination": "Where to place the runtime within this repo",
        "force": "Overwrite destination if it already exists",
    },
)
def copy_runtime_pack(
    ctx,
    source,
    expected_sha256="",
    destination="runtime/lmstudio-rocm-1.55.0",
    force=False,
) -> None:
    """Copy + validate the LM Studio runtime pack."""
    cmd = [
        "uv",
        "run",
        "python",
        "infra/runtime/copy_runtime_pack.py",
        f'"{source}"',
        f'--destination "{destination}"',
    ]
    if expected_sha256:
        cmd.extend(["--expected-sha256", expected_sha256])
    if force:
        cmd.append("--force")
    ctx.run(" ".join(cmd), echo=True, pty=True)


@task(pre=[lint_backend, lint_frontend, test_backend])
def ci(ctx) -> None:  # noqa: ARG001
    """Aggregate task mirroring the Phase 1 CI workflow."""
    print("All checks passed.")
