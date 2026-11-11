from __future__ import annotations
import json
from pathlib import Path
import sqlite3
from gamestick_ai.catalog import init_demo_db, upsert_games
from gamestick_ai.models import Game


def create_demo(root: Path, package: Path) -> None:
    if root.exists() or package.exists():
        raise FileExistsError("Demo paths must not already exist; nothing overwritten")
    root.mkdir(parents=True)
    (root / "roms/nes").mkdir(parents=True)
    (root / "covers/nes").mkdir(parents=True)
    (root / ".gamestick-demo.json").write_text(json.dumps({"profile":"demo-v1"}),encoding="utf-8")
    init_demo_db(root / "game/games.db")
    # Public-domain-style fake binary fixture, NOT a game ROM or commercial asset.
    (root / "roms/nes/sample.nes").write_bytes(b"NES-DEMO-FIXTURE-ONLY")
    upsert_games(root / "game/games.db", [Game("nes", "Sample Demo", "roms/nes/sample.nes", "", 1)])
    with sqlite3.connect(root / "game/games.db") as con:
        con.execute("UPDATE games SET favorite=1 WHERE title=?", ("Sample Demo",))
    package.mkdir(parents=True)
    (package / "demo_game.nes").write_bytes(b"NES-DEMO-NEW-ROM-NOT-PLAYABLE")
    (package / "games.json").write_text(json.dumps({"games":[
        {"system":"nes", "title":"New Demo", "source":"demo_game.nes"}
    ]},indent=2),encoding="utf-8")
