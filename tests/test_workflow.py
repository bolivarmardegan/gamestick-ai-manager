import json
import sqlite3
import pytest
from pathlib import Path
from gamestick_ai.apply import apply_plan, CONFIRMATION
from gamestick_ai.backup import backup
from gamestick_ai.catalog import list_games
from gamestick_ai.fs import safe_child
from gamestick_ai.gamification import badge_report
from gamestick_ai.inventory import inventory
from gamestick_ai.planner import make_plan
from gamestick_ai.restore import restore, RESTORE_PHRASE


def test_inventory(example):
    card,pkg,backups=example
    result=inventory(card)
    assert result['total']==1 and result['favorites']==1
    assert not result['warnings']


def test_plan_does_not_mutate(example):
    card,pkg,backups=example
    original=card.db.read_bytes()
    plan=make_plan(card,pkg)
    assert plan['deletions']==0
    assert card.db.read_bytes()==original
    assert not (card.root/'roms/nes/new-demo.nes').exists()


def test_backup_reuses_verified_copy(example):
    card,pkg,backups=example
    first=backup(card,backups)
    second=backup(card,backups)
    assert first['status']=='created' and second['status']=='reused'
    assert second['path']==first['path']


def test_apply_requires_backup_and_confirmation(example):
    card,pkg,backups=example
    with pytest.raises(PermissionError):
        apply_plan(card,pkg,backups,execute=True,confirmation=CONFIRMATION)
    backup(card,backups)
    with pytest.raises(PermissionError):
        apply_plan(card,pkg,backups,execute=True)
    result=apply_plan(card,pkg,backups,execute=False)
    assert result['status']=='dry-run'


def test_apply_preserves_favorites_and_restores(example):
    card,pkg,backups=example
    saved=backup(card,backups)
    result=apply_plan(card,pkg,backups,execute=True,confirmation=CONFIRMATION)
    assert result['status']=='applied'
    games=list_games(card.db)
    assert len(games)==2
    assert next(x.favorite for x in games if x.title=='Sample Demo')==1
    assert (card.root/'roms/nes/new-demo.nes').exists()
    dry=restore(card,Path(saved['path']))
    assert dry['status']=='dry-run'
    restore(card,Path(saved['path']),execute=True,confirmation=RESTORE_PHRASE)
    assert len(list_games(card.db))==1


def test_traversal_and_symlinks_forbidden(example,tmp_path):
    card,pkg,backups=example
    with pytest.raises(ValueError): safe_child(card.root,'../../etc/passwd')
    (pkg/'escape.nes').symlink_to(pkg/'demo_game.nes')
    (pkg/'games.json').write_text(json.dumps({'games':[{'system':'nes','title':'X',
        'source':'escape.nes'}]}))
    with pytest.raises(ValueError): make_plan(card,pkg)


def test_gamification():
    report=badge_report(verified_backup=True,cataloged=2,planned=1)
    assert report['xp']==50
