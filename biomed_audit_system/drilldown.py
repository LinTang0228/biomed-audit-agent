"""
Render Layer 2 detail for findings in a saved CombinedReport JSON. No model needed.

First produce a report with the full system and save its JSON:
    python -m biomed_audit_system.run_audit script.R
    # copy the JSON block it prints into report.json

Then drill down:
    python -m biomed_audit_system.drilldown report.json F3
    python -m biomed_audit_system.drilldown report.json --severity Critical
    python -m biomed_audit_system.drilldown report.json --all
"""
import json
import sys
from pathlib import Path

from .layer2 import render_layer2
from .schema import CombinedReport

_USAGE = (
    "Usage: python -m biomed_audit_system.drilldown report.json "
    "<F-id ... | --severity SEV | --area AREA | --all>"
)


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 2:
        print(_USAGE)
        sys.exit(1)

    report = CombinedReport(**json.loads(Path(args[0]).read_text(encoding="utf-8")))
    selector = args[1]

    if selector == "--all":
        print(render_layer2(report))
    elif selector == "--severity" and len(args) >= 3:
        print(render_layer2(report, severity=args[2]))
    elif selector == "--area" and len(args) >= 3:
        print(render_layer2(report, area=args[2]))
    elif selector.startswith("--"):
        print(_USAGE)
        sys.exit(1)
    else:
        print(render_layer2(report, ids=args[1:]))


if __name__ == "__main__":
    main()
