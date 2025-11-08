#!/usr/bin/env python3
"""Fetch and build llama.cpp with ROCm acceleration."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/ggerganov/llama.cpp.git"
DEFAULT_REF = "master"
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / ".runtime" / "llama.cpp"
DEFAULT_BUILD = ROOT / ".runtime" / "build-rocm"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    """Run a shell command and stream output."""
    print(f"[build] {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def ensure_repo(source_dir: Path, repo_url: str, ref: str) -> None:
    """Clone or update llama.cpp to the requested ref."""
    if not source_dir.exists():
        source_dir.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", repo_url, str(source_dir)])
    run(["git", "fetch", "--all", "--tags"], cwd=source_dir)
    run(["git", "checkout", ref], cwd=source_dir)
    run(["git", "submodule", "update", "--init", "--recursive"], cwd=source_dir)


def configure_build(build_dir: Path, source_dir: Path, generator: str | None, hip_path: str | None) -> None:
    """Set up the ROCm build directory."""
    build_dir.mkdir(parents=True, exist_ok=True)
    cmd: list[str] = [
        "cmake",
        "-S",
        str(source_dir),
        "-B",
        str(build_dir),
        "-DLLAMA_HIPBLAS=1",
        "-DLLAMA_CLBLAST=0",
        "-DLLAMA_BUILD_SERVER=ON",
        "-DLLAMA_NATIVE=OFF",
        "-DLLAMA_CUBLAS=0",
        "-DLLAMA_METAL=0",
        "-DCMAKE_BUILD_TYPE=Release",
    ]
    if generator:
        cmd.extend(["-G", generator])
    if hip_path:
        cmd.append(f"-DHIP_PATH={hip_path}")
    run(cmd)


def build(build_dir: Path, target: str | None) -> None:
    """Invoke CMake build."""
    cmd = ["cmake", "--build", str(build_dir), "--config", "Release"]
    if target:
        cmd.extend(["--target", target])
    run(cmd)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-url", default=REPO_URL, help="Git URL for llama.cpp")
    parser.add_argument("--ref", default=DEFAULT_REF, help="Git ref/tag to check out")
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Directory where llama.cpp should live",
    )
    parser.add_argument(
        "--build-dir",
        type=Path,
        default=DEFAULT_BUILD,
        help="Directory for the ROCm build artifacts",
    )
    parser.add_argument("--generator", help="Optional CMake generator (e.g. Ninja)")
    parser.add_argument("--hip-path", help="Explicit HIP toolchain path override")
    parser.add_argument("--target", default="llama", help="CMake target to build")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_repo(args.source_dir, args.repo_url, args.ref)
    configure_build(args.build_dir, args.source_dir, args.generator, args.hip_path)
    build(args.build_dir, args.target)
    print(f"Build complete. Artifacts available in: {args.build_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
