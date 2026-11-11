from __future__ import annotations
import shutil
import sqlite3
import tempfile
from pathlib import Path
from gamestick_ai.backup import latest_verified
from gamestick_ai.catalog import upsert_games
from gamestick_ai.config import Settings
from gamestick_ai.fs import atomic_copy, checksum, safe_child
from gamestick_ai.models import Game
from gamestick_ai.planner import make_plan

CONFIRMATION='APPLY DEMO CHANGES'


def apply_plan(settings:Settings, package:Path, backup_dir:Path, *, execute:bool,
               confirmation:str='') -> dict:
    plan=make_plan(settings,package)
    if not execute:
        return {'status':'dry-run','plan':plan}
    if confirmation != CONFIRMATION:
        raise PermissionError('Explicit user confirmation required')
    backup_path=latest_verified(backup_dir.expanduser().resolve(),settings.root,require_current=True)
    if not backup_path:
        raise PermissionError('No verified backup found; run backup first')
    # Never trust the earlier plan without revalidating sources and hashes.
    for item in plan['operations']:
        src=Path(item['source'])
        if checksum(src)!=item['sha256'] or src.stat().st_size!=item['bytes']:
            raise RuntimeError('Source ROM changed since planning')
        if item['cover_source'] and checksum(Path(item['cover_source']))!=item['cover_sha256']:
            raise RuntimeError('Cover changed since planning')
    # Prepare DB locally, preserving any original favorite flags and untouched entries.
    with tempfile.TemporaryDirectory(prefix='gamestick-db-') as temp:
        candidate=Path(temp)/'games.db'
        shutil.copy2(settings.db,candidate)
        records=[Game(item['system'],item['title'],item['target'],item['cover_target'] or '')
                 for item in plan['operations']]
        upsert_games(candidate,records)
        with sqlite3.connect(candidate) as con:
            if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
                raise RuntimeError('Staged DB failed integrity check')
        # ROMs and covers are installed FIRST; SQLite database LAST.
        for item in plan['operations']:
            atomic_copy(Path(item['source']),safe_child(settings.root,item['target']))
            if item['cover_source']:
                atomic_copy(Path(item['cover_source']),safe_child(settings.root,item['cover_target']))
        atomic_copy(candidate,settings.db)
    return {'status':'applied','games':len(records),'backup':str(backup_path),
            'note':'Restore from backup if interrupted; no automatic rollback of partial copies'}
