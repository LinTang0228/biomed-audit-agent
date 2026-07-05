"""
Evaluation scorer (deterministic; no ADK, no model).

Scores saved system reports against `answer_key.json` at rule-id granularity per
fixture, and prints a scorecard: per-fixture TP/FP/FN, pooled precision/recall,
recall by severity, and severity agreement on matched rules. Controls are scored
separately (any Critical/Important finding is a false positive; a Minor is
tolerated).

The `reports/` directory is produced by `run_all.py` (a live run) or by
`run_audit --json`. This module needs no model.

Usage:
    python -m biomed_audit_system.eval.evaluate               # reports/ dir default
    python -m biomed_audit_system.eval.evaluate path/to/reports_dir
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

_HERE = Path(__file__).resolve().parent
_MAJOR = {"Critical", "Important"}


def _load_answer_key() -> dict:
    return json.loads((_HERE / "answer_key.json").read_text(encoding="utf-8"))


def _reported_rule_severity(report: dict) -> Dict[str, str]:
    """First-seen severity per rule_id in a system report."""
    out: Dict[str, str] = {}
    for f in report.get("findings", []):
        out.setdefault(f["rule_id"], f["severity"])
    return out


def score_fixture(spec: dict, report: dict) -> dict:
    reported = _reported_rule_severity(report)
    if spec.get("is_control"):
        fp_rules = [r for r, sev in reported.items() if sev in _MAJOR]
        return {"control": True, "tp": 0, "fp": len(fp_rules), "fn": 0,
                "fp_rules": fp_rules, "tolerated_minor": [r for r, sev in reported.items() if sev not in _MAJOR]}

    expected = {e["rule_id"]: e["severity"] for e in spec["expected"]}
    exp_rules, rep_rules = set(expected), set(reported)
    matched = exp_rules & rep_rules
    fp = sorted(rep_rules - exp_rules)
    fn = sorted(exp_rules - rep_rules)
    sev_agree = sum(1 for r in matched if expected[r] == reported[r])
    return {"control": False, "tp": len(matched), "fp": len(fp), "fn": len(fn),
            "fp_rules": fp, "fn_rules": fn, "matched": sorted(matched),
            "sev_agree": sev_agree, "sev_total": len(matched),
            "expected": expected, "reported": reported}


def _pct(n: int, d: int) -> str:
    return f"{(n / d):.2f}" if d else "  -"


def evaluate(reports_dir: Path) -> None:
    key = _load_answer_key()["fixtures"]
    rows, missing = [], []
    tp = fp = fn = 0
    sev_agree = sev_total = 0
    # recall by expected severity
    rec_hit = {"Critical": 0, "Important": 0, "Minor": 0}
    rec_tot = {"Critical": 0, "Important": 0, "Minor": 0}
    ctrl_fp = 0

    for fixture, spec in key.items():
        rpath = reports_dir / (fixture + ".json")
        if not rpath.exists():
            missing.append(fixture)
            continue
        report = json.loads(rpath.read_text(encoding="utf-8"))
        r = score_fixture(spec, report)
        rows.append((fixture, r))
        if r["control"]:
            ctrl_fp += r["fp"]
            continue
        tp += r["tp"]; fp += r["fp"]; fn += r["fn"]
        sev_agree += r["sev_agree"]; sev_total += r["sev_total"]
        for rid, sev in r["expected"].items():
            rec_tot[sev] += 1
            if rid in r["reported"]:
                rec_hit[sev] += 1

    # ---- scorecard ----
    print("Per-fixture (non-control)")
    print(f"{'fixture':32} {'TP':>3} {'FP':>3} {'FN':>3}  prec  rec")
    for fixture, r in rows:
        if r["control"]:
            continue
        p = _pct(r["tp"], r["tp"] + r["fp"])
        rc = _pct(r["tp"], r["tp"] + r["fn"])
        print(f"{fixture:32} {r['tp']:>3} {r['fp']:>3} {r['fn']:>3}  {p}  {rc}")
        if r["fp_rules"]:
            print(f"    FP: {r['fp_rules']}")
        if r["fn_rules"]:
            print(f"    FN: {r['fn_rules']}")

    print("\nControls (expect no Critical/Important)")
    for fixture, r in rows:
        if not r["control"]:
            continue
        verdict = "OK (clean)" if r["fp"] == 0 else f"FAIL: {r['fp_rules']}"
        print(f"{fixture:32} major-FP={r['fp']}  {verdict}")

    print("\nPooled (non-control)")
    print(f"  precision = {_pct(tp, tp + fp)}   recall = {_pct(tp, tp + fn)}"
          f"   (TP={tp} FP={fp} FN={fn})")
    print(f"  control false positives (Critical/Important) = {ctrl_fp}")
    print("\nRecall by expected severity")
    for sev in ("Critical", "Important", "Minor"):
        print(f"  {sev:9} {rec_hit[sev]}/{rec_tot[sev]}  ({_pct(rec_hit[sev], rec_tot[sev])})")
    print(f"\nSeverity agreement on matched rules = {_pct(sev_agree, sev_total)}"
          f"  ({sev_agree}/{sev_total})")

    if missing:
        print(f"\n[!] {len(missing)} report(s) not found in {reports_dir} "
              f"(run run_all or run_audit --json first): {missing}")


def main() -> None:
    reports_dir = Path(sys.argv[1]) if len(sys.argv) >= 2 else (_HERE / "reports")
    evaluate(reports_dir)


if __name__ == "__main__":
    main()
