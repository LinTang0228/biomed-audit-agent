"""
Deterministic combiner (no ADK, no model).

Merges the per-checker findings into a single Layer 1 result. Being deterministic
makes it fully testable and removes model non-determinism from the merge step.

Steps:
1. Enforce scope: drop any finding whose `area` is outside the emitting checker's
   allowed areas (defence-in-depth against a checker straying out of scope), and
   count how many were dropped.
2. De-duplicate by (rule_id, location), keeping the most severe.
3. Sort Critical -> Important -> Minor, then by area and rule_id.
4. Assign global ids (F1, F2, ...) and count severities.
"""
from __future__ import annotations

from typing import Dict, List

from .schema import CombinedReport, Finding

# Which areas each checker is allowed to emit. Mirrors the checker registry.
CHECKER_AREAS: Dict[str, set] = {
    "stats_design": {"study_design", "statistics"},
    "repro_coding": {"data_handling", "reproducibility"},
    "interpretation": {"interpretation"},
    "leakage": {"modeling_evaluation"},
}

_SEV_ORDER = {"Critical": 0, "Important": 1, "Minor": 2}


def _as_dict(finding) -> dict:
    return finding if isinstance(finding, dict) else finding.model_dump()


def combine(
    per_checker: Dict[str, dict],
    language: str,
    analysis_types: List[str],
) -> CombinedReport:
    """`per_checker` maps checker name -> that checker's AuditFindings as a dict."""
    kept: List[dict] = []
    dropped = 0

    for checker, result in per_checker.items():
        allowed = CHECKER_AREAS.get(checker, set())
        for f in (result or {}).get("findings", []):
            f = _as_dict(f)
            if f.get("area") not in allowed:
                dropped += 1          # scope violation
                continue
            kept.append(f)

    deduped = _dedupe(kept)
    deduped.sort(
        key=lambda f: (_SEV_ORDER.get(f["severity"], 9), f["area"], f["rule_id"])
    )
    for i, f in enumerate(deduped, start=1):
        f["id"] = f"F{i}"

    counts = {
        s: sum(1 for f in deduped if f["severity"] == s)
        for s in ("Critical", "Important", "Minor")
    }

    return CombinedReport(
        language=language,
        analysis_types=analysis_types,
        checkers_run=list(per_checker.keys()),
        counts=counts,
        findings=[Finding(**f) for f in deduped],
        scope_violations_dropped=dropped,
    )


def _dedupe(findings: List[dict]) -> List[dict]:
    """Keep one finding per (rule_id, location), the most severe."""
    best: Dict[tuple, dict] = {}
    for f in findings:
        key = (f.get("rule_id"), f.get("location"))
        cur = best.get(key)
        if cur is None or _SEV_ORDER.get(f["severity"], 9) < _SEV_ORDER.get(cur["severity"], 9):
            best[key] = f
    return list(best.values())
