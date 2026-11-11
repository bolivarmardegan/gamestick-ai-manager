from __future__ import annotations
import json
import shutil
import uuid
from datetime import datetime,timezone
from pathlib import Path
from gamestick_ai.config import Settings
from gamestick_ai.fs import checksum, safe_child


def _entries(root: Path):
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            raise ValueError(f"Symlink detected: {p}")
        if p.is_file():
            yield p


def _verify(backup_dir: Path) -> bool:
    manifest = backup_dir / 'manifest.json'
    if not manifest.is_file():
        return False
    try:
        data=json.loads(manifest.read_text(encoding='utf-8'))
        return bool(data.get('files')) and all(
            safe_child(backup_dir/'card',item['path']).is_file() and
            checksum(safe_child(backup_dir/'card',item['path'])) == item['sha256']
            for item in data['files']
        )
    except (ValueError,KeyError,OSError,TypeError):
        return False


def backup(settings:Settings, destination:Path) -> dict:
    destination=destination.expanduser().resolve()
    if destination==settings.root or destination.is_relative_to(settings.root):
        raise ValueError('Backup destination must be outside the card')
    destination.mkdir(parents=True,exist_ok=True)
    # Skip completed verified backups of the same source state; never freeze at 99.9%.
    current=list(_entries(settings.root))
    current_hash={str(p.relative_to(settings.root)):checksum(p) for p in current}
    for d in sorted(destination.glob('backup-*')):
        if _verify(d):
            manifest=json.loads((d/'manifest.json').read_text())
            if manifest.get('source')==str(settings.root) and {
                x['path']:x['sha256'] for x in manifest['files']}==current_hash:
                return {'status':'reused', 'path':str(d), 'files':len(current)}
    target=destination/('backup-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:6])
    target.mkdir(parents=True,exist_ok=False)
    try:
        entries=[]
        for p in current:
            rel=str(p.relative_to(settings.root))
            to=safe_child(target/'card',rel) if (target/'card').exists() else target/'card'/rel
            to.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(p,to,follow_symlinks=False)
            if checksum(to)!=current_hash[rel]:
                raise RuntimeError('Backup checksum mismatch')
            entries.append({'path':rel,'sha256':current_hash[rel],'size':p.stat().st_size})
        data={'source':str(settings.root),'created_at':datetime.now(timezone.utc).isoformat(), 'files':entries}
        (target/'manifest.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
        if not _verify(target):
            raise RuntimeError('Backup verification failed')
        return {'status':'created','path':str(target),'files':len(entries)}
    except Exception:
        shutil.rmtree(target,ignore_errors=True)
        raise


def latest_verified(destination:Path, source:Path, *, require_current: bool = False) -> Path | None:
    if not destination.exists():
        return None
    candidates=sorted(destination.glob('backup-*'),reverse=True)
    for d in candidates:
        if _verify(d) and json.loads((d/'manifest.json').read_text()).get('source')==str(source):
            if require_current:
                current = {str(f.relative_to(source)):checksum(f) for f in _entries(source)}
                recorded = {f['path']:f['sha256'] for f in json.loads((d/'manifest.json').read_text())['files']}
                if recorded != current:
                    continue
            return d
    return None
