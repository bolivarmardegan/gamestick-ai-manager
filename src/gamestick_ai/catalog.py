from __future__ import annotations
import sqlite3
from pathlib import Path
from gamestick_ai.models import Game

DDL = """
CREATE TABLE IF NOT EXISTS games (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  system TEXT NOT NULL,
  title TEXT NOT NULL,
  rom_path TEXT NOT NULL,
  cover_path TEXT NOT NULL DEFAULT '',
  favorite INTEGER NOT NULL DEFAULT 0 CHECK (favorite IN (0,1)),
  UNIQUE(system,title)
);
"""


def init_demo_db(db: Path) -> None:
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as con:
        con.executescript(DDL)


def list_games(db: Path) -> list[Game]:
    with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute("SELECT system,title,rom_path,cover_path,favorite FROM games ORDER BY system,title")
        return [Game(**dict(row)) for row in rows]


def upsert_games(db: Path, games: list[Game]) -> None:
    # Do not update favorite. That preserves favorite (including 'R2' style favourites) on replacement.
    with sqlite3.connect(db) as con:
        con.execute("BEGIN IMMEDIATE")
        for g in games:
            con.execute("""INSERT INTO games(system,title,rom_path,cover_path,favorite)
                VALUES (?,?,?,?,0) ON CONFLICT(system,title) DO UPDATE SET
                rom_path=excluded.rom_path, cover_path=excluded.cover_path""",
                (g.system,g.title,g.rom_path,g.cover_path))
        con.commit()
