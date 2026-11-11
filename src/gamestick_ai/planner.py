from __future__ import annotations
import json
import re
from pathlib import Path
from gamestick_ai.config import (IMAGE_TYPES, MAX_ITEM_BYTES, MAX_PACKAGE_BYTES,
                                 MAX_PACKAGE_ITEMS, SYSTEMS, Settings)
from gamestick_ai.fs import checksum, safe_child
from gamestick_ai.models import PlannedGame


def _stem(title:str) -> str:
    stem=re.sub(r'[^a-zA-Z0-9_-]+','-',title.strip()).strip('-').lower()
    if not stem or len(stem)>70:
        raise ValueError('Invalid game title or overly long slug')
    return stem


def make_plan(settings:Settings, package:Path) -> dict:
    package=package.expanduser().resolve(strict=True)
    data=json.loads(safe_child(package,'games.json').read_text(encoding='utf-8'))
    specs=data.get('games')
    if not isinstance(specs,list) or not (1<=len(specs)<=MAX_PACKAGE_ITEMS):
        raise ValueError('Invalid package game count')
    items=[];seen=set();total_bytes=0;targets=set()
    for obj in specs:
        if not isinstance(obj,dict):
            raise ValueError('Invalid game entry')
        system=obj.get('system');title=obj.get('title');rel=obj.get('source')
        if not isinstance(system,str) or system not in SYSTEMS:
            raise ValueError(f'Unknown system: {system}')
        if not isinstance(title,str) or not title.strip() or len(title)>90:
            raise ValueError('Invalid title')
        if not isinstance(rel,str):
            raise ValueError('Missing source')
        src=safe_child(package,rel)
        if not src.is_file() or src.suffix.lower() not in SYSTEMS[system]:
            raise ValueError(f'Invalid ROM for {system}: {rel}')
        size=src.stat().st_size
        if size<=0 or size>MAX_ITEM_BYTES:
            raise ValueError('ROM size exceeds policy')
        key=(system,title.casefold())
        if key in seen:
            raise ValueError('Duplicate game in package')
        seen.add(key)
        target=f'roms/{system}/{_stem(title)}{src.suffix.lower()}'
        cover_rel=obj.get('cover');cover_target=None;cover_hash=None
        if cover_rel is not None:
            if not isinstance(cover_rel,str): raise ValueError('Invalid cover')
            cover=safe_child(package,cover_rel)
            if not cover.is_file() or cover.suffix.lower() not in IMAGE_TYPES:
                raise ValueError('Invalid cover file')
            cover_target=f'covers/{system}/{_stem(title)}{cover.suffix.lower()}'
            cover_hash=checksum(cover)
            total_bytes+=cover.stat().st_size
        else: cover=None
        if target in targets or (cover_target and cover_target in targets):
            raise ValueError('Target collision')
        targets.add(target)
        if cover_target: targets.add(cover_target)
        total_bytes+=size
        items.append(PlannedGame(system,title,str(src),target,checksum(src),size,
                                str(cover) if cover else None,cover_target,cover_hash))
    if total_bytes>MAX_PACKAGE_BYTES:
        raise ValueError('Package size exceeds policy')
    # Revalidate no target symlinks exist.
    for item in items:
        safe_child(settings.root,item.target)
        if item.cover_target: safe_child(settings.root,item.cover_target)
    return {'profile':settings.profile,'card':str(settings.root),'package':str(package),
            'operations':[i.as_dict() for i in items],'total_bytes':total_bytes,
            'mode':'dry-run','deletions':0,'requires_backup':True,
            'warning':'Only the demo-v1 card is supported for writes'}
