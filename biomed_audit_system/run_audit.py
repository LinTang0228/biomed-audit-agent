"""
Run the full audit system on one script: print the Layer 1 summary, and
optionally save the report JSON and/or the self-contained HTML report.

Usage (run as a module so package imports resolve):
    python -m biomed_audit_system.run_audit script.R
    python -m biomed_audit_system.run_audit script.R --json report.json --html report.html

Requires a Gemini API key (AI Studio): set GOOGLE_API_KEY and BIOAUDIT_MODEL.
Cannot run without a live model. The saved JSON feeds `drilldown`, `render_report`,
and the evaluation harness; the HTML is the shareable report.
"""
import asyncio
import sys
from pathlib import Path

from .html_report import render_html
from .orchestrator import audit
from .util import render_layer1


def _opt(args, name):
    return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else None


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0].startswith("--"):
        print("Usage: python -m biomed_audit_system.run_audit script [--json out.json] [--html out.html]")
        sys.exit(1)

    path = args[0]
    json_out = _opt(args, "--json")
    html_out = _opt(args, "--html")

    code = Path(path).read_text(encoding="utf-8")
    report = asyncio.run(audit(code, filename=path))

    print(render_layer1(report))

    if json_out:
        Path(json_out).write_text(report.model_dump_json(indent=2), encoding="utf-8")
        print(f"[saved report JSON -> {json_out}]")
    if html_out:
        Path(html_out).write_text(render_html(report, source=Path(path).name), encoding="utf-8")
        print(f"[saved HTML report -> {html_out}]")
    if not (json_out or html_out):
        print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
