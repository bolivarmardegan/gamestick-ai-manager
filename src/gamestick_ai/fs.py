from __future__ import annotations
import hashlib
import os
import shutil
from pathlib import Path


def checksum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def safe_child(base: Path, relative: str) -> Path:
    """Disallow absolute paths, traversal, and symlinks in every existing parent."""
    base = base.resolve(strict=True)
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or any(part in ("..", ".") for part in rel.parts):
        raise ValueError(f"Unsafe path: {relative}")
    target = base.joinpath(*rel.parts)
    cursor = base
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError(f"Symlinks forbidden: {cursor}")
    if not target.resolve(strict=False).is_relative_to(base):
        raise ValueError("Path escapes approved root")
    return target


def atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_name(destination.name + ".gamestick-tmp")
    if tmp.exists():
        raise ValueError(f"Temporary path already exists: {tmp}")
    try:
        with source.open("rb") as src, tmp.open("xb") as dst:
            shutil.copyfileobj(src, dst, 1024 * 1024)
            dst.flush()
            os.fsync(dst.fileno())
        if checksum(source) != checksum(tmp):
            raise RuntimeError("Copy verification failed")
        os.replace(tmp, destination)
    finally:
        if tmp.exists():
            tmp.unlink()
