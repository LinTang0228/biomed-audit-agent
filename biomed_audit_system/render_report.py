"""
Render a saved CombinedReport JSON to a self-contained HTML file. No model needed.

First produce a report with the full system and save its JSON:
    python -m biomed_audit_system.run_audit script.R
    # copy the JSON block it prints into report.json

Then render the report:
    python -m biomed_audit_system.render_report report.json report.html
    python -m biomed_audit_system.render_report report.json report.html "fhs_04_coding_bugs.R"

The third argument (optional) is the source label shown in the header; it defaults
to "analysis script".
"""
import json
import sys
from pathlib import Path

from .html_report import render_html
from .schema import CombinedReport

_USAGE = (
    "Usage: python -m biomed_audit_system.render_report "
    "report.json out.html [source_label]"
)


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 2:
        print(_USAGE)
        sys.exit(1)

    report = CombinedReport(**json.loads(Path(args[0]).read_text(encoding="utf-8")))
    source = args[2] if len(args) >= 3 else "analysis script"
    html = render_html(report, source=source)
    Path(args[1]).write_text(html, encoding="utf-8")
    print(f"Wrote {args[1]} ({len(html)} bytes).")


if __name__ == "__main__":
    main()
