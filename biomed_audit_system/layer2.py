"""
Layer 2 — drill-down detail (Stage 4). Deterministic; no ADK, no model.

Each finding produced by a checker already carries `what`, `why`, `fix_kind`, and
a before/after `suggestion`. This module presents that detail on demand for a
selected finding (or set), adds the trust framing (mechanical vs substantive) and
the standard "read-not-run" caveat, and validates the suggestion. Because it works
from the finished report, it is fully testable without a live model.
"""
from __future__ import annotations

from typing import List, Optional

from .schema import CombinedReport, Finding

_RULE = "-" * 68

_TRUST = {
    "mechanical": (
        "MECHANICAL - a single correct local edit; safe to apply after a quick check."
    ),
    "substantive": (
        "SUBSTANTIVE - changes the scientific content of the analysis; review the "
        "reasoning before accepting."
    ),
}

_CAVEAT = (
    "Note: this tool read the code but did not run it. Treat the fix as a reviewed "
    "proposal, not a verified result - re-run the corrected script to confirm."
)


def validate_suggestion(f: Finding) -> Optional[str]:
    """Return a short warning if the suggestion looks malformed, else None."""
    s = (f.suggestion or "").strip()
    if len(s) < 12:
        return "suggestion is empty or too short"
    signals = ["-", "+", "before", "after", "->", "```", "<-", "="]
    if not any(sig in s.lower() for sig in signals):
        return "suggestion has no clear before/after"
    return None


def _indent(text: str, n: int = 4) -> str:
    pad = " " * n
    return "\n".join(pad + line for line in text.splitlines())


def render_finding_detail(f: Finding) -> str:
    warn = validate_suggestion(f)
    lines = [
        _RULE,
        f"[{f.severity}] {f.title}    (id {f.id}, {f.rule_id}, {f.confidence})",
        f"Area: {f.area}",
        f"Location: {f.location}",
        "",
        f"What: {f.what}",
        f"Why:  {f.why}",
        "",
        f"Suggested fix - {_TRUST.get(f.fix_kind, f.fix_kind)}",
        _indent(f.suggestion or ""),
    ]
    if warn:
        lines.append(f"    [!] {warn}")
    lines += ["", _CAVEAT]
    return "\n".join(lines)


def select_findings(
    report: CombinedReport,
    ids: Optional[List[str]] = None,
    severity: Optional[str] = None,
    area: Optional[str] = None,
) -> List[Finding]:
    findings = list(report.findings)
    if ids:
        idset = set(ids)
        findings = [f for f in findings if f.id in idset]
    if severity:
        findings = [f for f in findings if f.severity == severity]
    if area:
        findings = [f for f in findings if f.area == area]
    return findings


def render_layer2(
    report: CombinedReport,
    ids: Optional[List[str]] = None,
    severity: Optional[str] = None,
    area: Optional[str] = None,
) -> str:
    findings = select_findings(report, ids=ids, severity=severity, area=area)
    if not findings:
        return "No matching findings.\n"
    return "\n\n".join(render_finding_detail(f) for f in findings) + "\n"
