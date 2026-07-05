"""Pure helpers (no ADK dependency): message construction and Layer 1 rendering."""
from __future__ import annotations

from pathlib import Path


def number_lines(code: str) -> str:
    """Prefix each line with 'N| ' so the model can cite real line numbers."""
    return "\n".join(f"{i + 1}| {ln}" for i, ln in enumerate(code.splitlines()))


def build_message(script_text: str, filename: str = "") -> str:
    name = Path(filename).name if filename else "script"
    return (
        f"Audit this script. File: {name}\n"
        f"Lines are prefixed with 'N| ' for reference; cite those numbers.\n"
        f"----- BEGIN SCRIPT -----\n{number_lines(script_text)}\n----- END SCRIPT -----"
    )


def render_layer1(report) -> str:
    """Render a CombinedReport as the Layer 1 summary text (see SKILL.md)."""
    c = report.counts
    lines = [
        "BIOMED ANALYSIS AUDIT — Layer 1 summary",
        f"Language: {report.language}   "
        f"Analysis: {', '.join(report.analysis_types) or 'unknown'}",
        f"Checkers: {', '.join(report.checkers_run)}",
        f"Findings: {c.get('Critical', 0)} Critical, "
        f"{c.get('Important', 0)} Important, {c.get('Minor', 0)} Minor",
        "",
    ]
    for sev in ("Critical", "Important", "Minor"):
        group = [f for f in report.findings if f.severity == sev]
        if not group:
            continue
        lines.append(sev.upper())
        for f in group:
            lines.append(
                f"  [{f.severity}] [{f.area}] {f.title} "
                f"— {f.location}  ({f.rule_id}, {f.confidence})"
            )
        lines.append("")
    if report.scope_violations_dropped:
        lines.append(
            f"(note: {report.scope_violations_dropped} out-of-scope finding(s) "
            f"were dropped by the combiner)"
        )
    return "\n".join(lines).rstrip() + "\n"
