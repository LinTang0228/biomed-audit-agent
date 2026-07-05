"""
Run the statistics & study-design checker on one script and print the Layer 1
summary plus the raw findings JSON.

Usage:
    python run_checker.py path/to/script.R

Requires a Gemini API key in the environment (AI Studio): set GOOGLE_API_KEY
(and, if your ADK build uses it, GOOGLE_GENAI_USE_VERTEXAI=FALSE).

This cannot run without a live model. The ADK/session APIs vary by version; if a
call signature differs, prefer running the agent via the ADK dev UI ('adk web')
instead — see STAGE2_README.md.
"""
import asyncio
import json
import sys
from pathlib import Path

APP = "biomed_audit"
_SEV_ORDER = {"Critical": 0, "Important": 1, "Minor": 2}


def number_lines(code: str) -> str:
    """Prefix each line with 'N| ' so the model can cite real line numbers."""
    return "\n".join(f"{i + 1}| {ln}" for i, ln in enumerate(code.splitlines()))


def build_message(path: str) -> str:
    code = Path(path).read_text(encoding="utf-8")
    return (
        f"Audit this script. File: {Path(path).name}\n"
        f"Lines are prefixed with 'N| ' for reference; cite those numbers.\n"
        f"----- BEGIN SCRIPT -----\n{number_lines(code)}\n----- END SCRIPT -----"
    )


def print_summary(data: dict) -> None:
    findings = sorted(
        data.get("findings", []),
        key=lambda f: _SEV_ORDER.get(f.get("severity", ""), 9),
    )
    print(f"\nLanguage: {data.get('language')}   "
          f"Analysis: {data.get('analysis_type')}")
    print(f"Findings: {len(findings)}\n")
    for f in findings:
        print(f"[{f['severity']:9}] [{f['area']}] {f['title']} "
              f"— {f['location']}  ({f['rule_id']}, {f['confidence']})")
    print()


async def audit(path: str) -> dict:
    # ADK imports are deferred so this module can be imported (and its helpers
    # tested) without google-adk installed.
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    from stats_design_checker.agent import root_agent

    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP, user_id="u", session_id="s")
    runner = Runner(agent=root_agent, app_name=APP, session_service=session_service)

    content = types.Content(role="user", parts=[types.Part(text=build_message(path))])
    result_text = None
    async for event in runner.run_async(user_id="u", session_id="s", new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            result_text = event.content.parts[0].text
    if result_text is None:
        raise RuntimeError("No final response from the agent.")
    return json.loads(result_text)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python run_checker.py path/to/script")
        sys.exit(1)
    data = asyncio.run(audit(sys.argv[1]))
    print_summary(data)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
