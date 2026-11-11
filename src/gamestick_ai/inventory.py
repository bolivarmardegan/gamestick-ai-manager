from __future__ import annotations
from gamestick_ai.catalog import list_games
from gamestick_ai.config import Settings
from gamestick_ai.fs import safe_child


def inventory(settings: Settings) -> dict:
    games = list_games(settings.db)
    warnings: list[str] = []
    for game in games:
        try:
            f = safe_child(settings.root, game.rom_path)
            if not f.is_file():
                warnings.append(f"Missing ROM: {game.rom_path}")
        except ValueError:
            warnings.append(f"Invalid ROM reference: {game.rom_path}")
    by_system: dict[str,int] = {}
    for g in games:
        by_system[g.system] = by_system.get(g.system,0)+1
    return {"root":str(settings.root), "profile":settings.profile,
            "total":len(games), "favorites":sum(g.favorite for g in games),
            "by_system":by_system, "warnings":warnings, "games":[g.as_dict() for g in games]}
