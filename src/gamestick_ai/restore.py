from __future__ import annotations
import json
from pathlib import Path
from gamestick_ai.backup import _verify
from gamestick_ai.config import Settings
from gamestick_ai.fs import atomic_copy,safe_child

RESTORE_PHRASE='RESTORE DEMO BACKUP'


def restore(settings:Settings, backup_dir:Path, *,execute:bool=False,confirmation:str='') -> dict:
    backup_dir=backup_dir.expanduser().resolve(strict=True)
    if not _verify(backup_dir):
        raise ValueError('Backup failed SHA-256 verification')
    data=json.loads((backup_dir/'manifest.json').read_text())
    if data['source']!=str(settings.root):
        raise ValueError('Backup source does not match card')
    if not execute:
        return {'status':'dry-run','files':len(data['files'])}
    if confirmation!=RESTORE_PHRASE:
        raise PermissionError('Explicit user confirmation required')
    # Restoration overlays backed-up files; it does not delete newly added files.
    for entry in data['files']:
        atomic_copy(safe_child(backup_dir/'card',entry['path']),
                    safe_child(settings.root,entry['path']))
    return {'status':'restored','files':len(data['files']),
            'note':'New files added after backup are not removed'}
