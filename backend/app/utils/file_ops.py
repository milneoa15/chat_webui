"""File-oriented helpers."""

from __future__ import annotations

import re
from hashlib import sha256
from pathlib import Path

from fastapi import UploadFile


async def save_upload(upload: UploadFile, destination: Path, chunk_size: int = 1024 * 1024) -> int:
    """Persist an UploadFile to disk and return the number of bytes written."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with destination.open("wb") as handle:
        while True:
            chunk = await upload.read(chunk_size)
            if not chunk:
                break
            handle.write(chunk)
            written += len(chunk)
    await upload.close()
    return written


def slugify(value: str) -> str:
    """Best-effort slug used to identify installed models."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or "model"


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def infer_quantization_from_filename(filename: str) -> str | None:
    """Try to infer the quant preset from a GGUF filename."""
    match = re.search(r"(q\d(?:_[a-z])?_?[a-z0-9]*)", filename.lower())
    if match:
        return match.group(1).upper()
    return None
