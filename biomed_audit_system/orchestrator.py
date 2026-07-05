"""
Orchestrator (Stage 3).

Ties the pieces together:
  triage (route)  ->  run selected checkers in parallel (ADK ParallelAgent)  ->
  deterministic combine  ->  Layer 1 report.

The three always-on checkers cover data-handling/reproducibility, study-design/
statistics, and interpretation; the leakage checker is added only for ML scripts.
ADK imports are deferred so `select_checkers` and the routing logic import and
test without ADK.
"""
from __future__ import annotations

import json
from typing import List

from .checkers import build_checker, output_key
from .combiner import combine
from .schema import CombinedReport
from .triage import Triage, classify
from .util import build_message

APP = "biomed_audit"
ALWAYS: List[str] = ["repro_coding", "stats_design", "interpretation"]


def select_checkers(triage: Triage) -> List[str]:
    names = list(ALWAYS)
    if triage.run_leakage:
        names.append("leakage")
    return names


async def audit(script_text: str, filename: str = "", model: str | None = None) -> CombinedReport:
    # Deferred ADK imports.
    from google.adk.agents import ParallelAgent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    triage = classify(script_text, filename)
    names = select_checkers(triage)
    checkers = [build_checker(n, model) for n in names]
    pool = ParallelAgent(name="checker_pool", sub_agents=checkers)

    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP, user_id="u", session_id="s")
    runner = Runner(agent=pool, app_name=APP, session_service=session_service)

    content = types.Content(
        role="user", parts=[types.Part(text=build_message(script_text, filename))]
    )
    async for _ in runner.run_async(user_id="u", session_id="s", new_message=content):
        pass  # each checker writes its structured findings to session.state[output_key]

    session = await session_service.get_session(app_name=APP, user_id="u", session_id="s")
    per_checker = {}
    for n in names:
        raw = session.state.get(output_key(n))
        if raw is None:
            continue
        per_checker[n] = raw if isinstance(raw, dict) else json.loads(raw)

    return combine(per_checker, triage.language, triage.analysis_types)
