from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from gamestick_ai.agents import Orchestrator
from gamestick_ai.apply import apply_plan
from gamestick_ai.backup import backup
from gamestick_ai.config import PROFILE,validate_root
from gamestick_ai.demo import create_demo
from gamestick_ai.inventory import inventory
from gamestick_ai.planner import make_plan
from gamestick_ai.restore import restore
from gamestick_ai.read_only import scan_card


def path_arg(p:str)->Path:
    return Path(p).expanduser()


def parser()->argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog='gamestick',description='GameStick AI Manager - safe demo POC')
    sub=p.add_subparsers(dest='command',required=True)
    x=sub.add_parser('demo',help='Create fake local card and fake game package')
    x.add_argument('--card',required=True,type=path_arg)
    x.add_argument('--package',required=True,type=path_arg)
    for name in ('inspect','backup','plan','apply','restore','ai-review'):
        s=sub.add_parser(name)
        s.add_argument('--card',required=True,type=path_arg)
        if name in ('plan','apply','ai-review'):
            s.add_argument('--package',required=True,type=path_arg)
        if name in ('backup','apply','ai-review'):
            s.add_argument('--backups',required=True,type=path_arg)
        if name=='restore':
            s.add_argument('--backup',required=True,type=path_arg)
        if name in ('apply','restore'):
            s.add_argument('--execute',action='store_true')
            s.add_argument('--confirm',default='',help='Explicit authorization phrase')
    scan=sub.add_parser('scan-card',help='Read-only scan of any mounted card directory')
    scan.add_argument('--mount',required=True,type=path_arg)
    sub.add_parser('profiles',help='Show implemented firmware adapters')
    return p


def main(argv:list[str]|None=None)->int:
    a=parser().parse_args(argv)
    try:
        if a.command=='scan-card': result=scan_card(a.mount)
        elif a.command=='profiles': result={'supported_for_writes':[PROFILE],
            'real_gamestick':'not implemented: firmware-specific review required'}
        elif a.command=='demo':
            create_demo(a.card,a.package)
            result={'card':str(a.card),'package':str(a.package),'status':'created'}
        else:
            settings=validate_root(a.card)
            if a.command=='inspect': result=inventory(settings)
            elif a.command=='backup': result=backup(settings,a.backups)
            elif a.command=='plan': result=make_plan(settings,a.package)
            elif a.command=='ai-review': result=Orchestrator().run(settings,a.package,a.backups,use_ai=True)
            elif a.command=='apply': result=apply_plan(settings,a.package,a.backups,
                    execute=a.execute,confirmation=a.confirm)
            elif a.command=='restore': result=restore(settings,a.backup,
                    execute=a.execute,confirmation=a.confirm)
            else: raise ValueError('Unknown command')
        print(json.dumps(result,indent=2,ensure_ascii=False,default=str))
        return 0
    except (ValueError,FileNotFoundError,FileExistsError,PermissionError,RuntimeError,OSError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
