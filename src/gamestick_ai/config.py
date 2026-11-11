from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path

# The supported profile in this POC is deliberately NOT the undocumented real GameStick schema.
PROFILE = "demo-v1"
SYSTEMS = {"nes": {".nes"}, "snes": {".sfc", ".smc"}, "gba": {".gba"},
           "genesis": {".md", ".bin", ".gen"}, "ps1": {".cue", ".chd", ".pbp"}}
IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp"}
MAX_PACKAGE_ITEMS = 50
MAX_ITEM_BYTES = 512 * 1024 * 1024
MAX_PACKAGE_BYTES = 2 * 1024 * 1024 * 1024


@dataclass(frozen=True)
class Settings:
    root: Path
    profile: str = PROFILE

    @property
    def db(self) -> Path:
        return self.root / "game" / "games.db"


def validate_root(root: Path) -> Settings:
    root = root.expanduser().resolve(strict=True)
    marker = root / ".gamestick-demo.json"
    if not marker.is_file() or marker.is_symlink():
        raise ValueError("Unsupported card: demo marker missing. Real firmware integration requires an audited adapter.")
    data = json.loads(marker.read_text(encoding="utf-8"))
    if data.get("profile") != PROFILE:
        raise ValueError("Unsupported profile; refusing to write")
    settings = Settings(root)
    if not settings.db.is_file() or settings.db.is_symlink():
        raise ValueError("Missing or unsafe game/games.db")
    return settings
