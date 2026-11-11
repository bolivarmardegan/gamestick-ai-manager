"""Read-only discovery of a physical card's *mounted directory* (no firmware assumptions)."""
from __future__ import annotations
import sqlite3
from collections import Counter
from pathlib import Path

ROM_EXTENSIONS={'.nes','.sfc','.smc','.gba','.gb','.gbc','.md','.gen','.cue','.chd','.pbp','.iso','.zip'}


def scan_card(root:Path, *,limit:int=25000)->dict:
    root=root.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Card mount path must be a directory')
    counts:Counter[str]=Counter()
    dbs=[]; warnings=[]; total=0
    for path in root.rglob('*'):
        if path.is_symlink():
            warnings.append('Symlink ignored')
            continue
        if not path.is_file():
            continue
        total+=1
        if total>limit:
            warnings.append(f'Scan stopped after {limit} files')
            break
        if path.suffix.lower() in ROM_EXTENSIONS:
            counts[path.suffix.lower()]+=1
        if path.name.lower() in {'games.db','database.sqlite3'}:
            relative=str(path.relative_to(root))
            try:
                con=sqlite3.connect(f'file:{path}?mode=ro&immutable=1',uri=True)
                try:
                    tables=[r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name LIMIT 40")]
                finally:con.close()
            except sqlite3.Error:
                tables=[]
                warnings.append(f'Could not inspect SQLite structure of {relative}')
            dbs.append({'path':relative,'table_names':tables})
    return {'mount':str(root),'scanned_files':min(total,limit),'rom_extensions':dict(counts),
            'sqlite_databases':dbs,'warnings':warnings,
            'writes_allowed':False,'note':'Read-only inventory; actual firmware mapping is not validated'}
