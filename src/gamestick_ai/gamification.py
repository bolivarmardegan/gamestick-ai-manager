from __future__ import annotations


def badge_report(*, verified_backup:bool, cataloged:int, planned:int, applied:int=0) -> dict:
    # Deterministic playful achievements; not real console game progression.
    achievements=[]
    if cataloged: achievements.append({'name':'Cartographer','points':10})
    if verified_backup: achievements.append({'name':'Backup Guardian','points':25})
    if planned: achievements.append({'name':'Careful Curator','points':15})
    if applied: achievements.append({'name':'Library Builder','points':20})
    return {'xp':sum(a['points'] for a in achievements),'badges':achievements}
