from __future__ import annotations
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Game:
    system: str
    title: str
    rom_path: str
    cover_path: str = ""
    favorite: int = 0

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SourceGame:
    system: str
    title: str
    source: Path
    cover: Path | None = None


@dataclass(frozen=True)
class PlannedGame:
    system: str
    title: str
    source: str
    target: str
    sha256: str
    bytes: int
    cover_source: str | None
    cover_target: str | None
    cover_sha256: str | None

    def as_dict(self) -> dict:
        return asdict(self)
