#!/usr/bin/env python3
"""Copy the LM Studio ROCm runtime pack into the repo with checksum verification."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DEST = ROOT / "runtime" / "lmstudio-rocm-1.55.0"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_dir(path: Path) -> str:
    digest = hashlib.sha256()
    for file_path in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(str(file_path.relative_to(path)).encode("utf-8"))
        digest.update(sha256_file(file_path).encode("utf-8"))
    return digest.hexdigest()


def copy_tree(source: Path, destination: Path, overwrite: bool) -> None:
    if destination.exists():
        if not overwrite:
            raise SystemExit(f"Destination {destination} already exists. Use --force to overwrite.")
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def persist_metadata(destination: Path, digest: str, version: str) -> None:
    metadata = {
        "version": version,
        "sha256": digest,
        "relative_path": str(destination.relative_to(ROOT)),
    }
    metadata_path = destination / "runtime-pack.json"
    with metadata_path.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
        handle.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Path to the LM Studio runtime directory or zip")
    parser.add_argument(
        "--destination",
        type=Path,
        default=DEFAULT_DEST,
        help="Where the runtime pack should be copied",
    )
    parser.add_argument(
        "--expected-sha256",
        help="Optional hash from LM Studio release notes for validation",
    )
    parser.add_argument("--version", default="1.55.0", help="Runtime pack version label")
    parser.add_argument("--force", action="store_true", help="Overwrite destination if it exists")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source
    if not source.exists():
        raise SystemExit(f"Source path {source} not found.")

    work_dir: Path
    cleanup_temp = False
    if source.is_file():
        tmp_dir = Path(tempfile.mkdtemp(prefix="lmstudio-pack-"))
        cleanup_temp = True
        shutil.unpack_archive(str(source), tmp_dir)
        work_dir = tmp_dir
    else:
        work_dir = source

    digest = sha256_dir(work_dir)
    if args.expected_sha256 and digest != args.expected_sha256:
        raise SystemExit(
            f"Hash mismatch! Expected {args.expected_sha256} but calculated {digest}.",
        )

    copy_tree(work_dir, args.destination, args.force)
    persist_metadata(args.destination, digest, args.version)
    if cleanup_temp:
        shutil.rmtree(work_dir, ignore_errors=True)
    print(f"Runtime pack copied to {args.destination} (sha256={digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
