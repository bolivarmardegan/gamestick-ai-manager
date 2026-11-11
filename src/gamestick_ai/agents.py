from __future__ import annotations
import json
import os
from pathlib import Path
from gamestick_ai.backup import latest_verified
from gamestick_ai.config import Settings
from gamestick_ai.gamification import badge_report
from gamestick_ai.inventory import inventory
from gamestick_ai.planner import make_plan

SYSTEM_PROMPT = """You are the GameStick guide. Explain the provided inventory and proposed changes.
SECURITY POLICY (must follow):
- This is a DEMO firmware profile, not a certified real device.
- You are read-only: no filesystem, shell, hardware or database tools are available.
- Never suggest bypassing backup or confirmation. Never authorize writes.
- Do not invent compatibility, ROM licensing, performance or successful device operations.
- Do not output file content, secrets or personal directories.
- Proposals must be clearly marked as simulation until user explicitly confirms in CLI.
- If warnings exist, mention them and recommend stopping until reviewed.
- Keep the answer concise and explain XP as simulated educational gamification.
"""


class InventoryAgent:
    """Deterministic inventory role, deliberately not an LLM."""
    def run(self, card:Settings)->dict:
        return inventory(card)


class SafetyAgent:
    """Deterministic planning role. LLM output cannot change these decisions."""
    def run(self, card:Settings, package:Path)->dict:
        return make_plan(card,package)


class GuideAgent:
    """Optional LangChain + ChatOpenAI narrator, no write tools."""
    def run(self, context:dict)->dict:
        if not os.getenv('OPENAI_API_KEY'):
            return {'mode':'offline','summary':f"Found {context['inventory']['total']} catalog entries; "
                    f"planned {len(context['plan']['operations'])} additions/replacements. "
                    "Back up and require confirmation before changes."}
        from langchain_openai import ChatOpenAI
        from pydantic import BaseModel

        class Review(BaseModel):
            summary: str
            risks: list[str]
            next_steps: list[str]

        llm=ChatOpenAI(model=os.getenv('GAMESTICK_AI_MODEL','gpt-4.1-mini'),temperature=0)
        # Minimize sensitive information sent to the model: no paths or full file manifest.
        minimal={'total_games':context['inventory']['total'],
                 'favorites':context['inventory']['favorites'],
                 'by_system':context['inventory']['by_system'],
                 'warning_count':len(context['inventory']['warnings']),
                 'planned_count':len(context['plan']['operations']),
                 'planned_bytes':context['plan']['total_bytes'],
                 'verified_backup':context['backed_up'],
                 'educational_xp':context['achievements']['xp']}
        response=llm.with_structured_output(Review).invoke([
            ('system',SYSTEM_PROMPT),
            ('human',json.dumps(minimal,ensure_ascii=False)),
        ])
        return {'mode':'langchain','review':response.model_dump()}


class Orchestrator:
    """Fixed-step mini orchestration: inventory -> safety -> guide -> badges."""
    def run(self, card:Settings, package:Path, backup_dir:Path, *, use_ai:bool)->dict:
        inv=InventoryAgent().run(card)
        plan=SafetyAgent().run(card,package)
        verified=latest_verified(backup_dir.expanduser().resolve(),card.root) is not None
        achievements=badge_report(verified_backup=verified,cataloged=inv['total'],
                                  planned=len(plan['operations']))
        context={'inventory':inv,'plan':plan,'backed_up':verified,'achievements':achievements}
        guide=GuideAgent().run(context) if use_ai else {'mode':'disabled','summary':'AI disabled'}
        # The guide's result is never fed to the executor.
        return {'analysis':context,'guide':guide,'write_authorized':False}
