"""
Self-contained HTML report (Stage 5). Deterministic; no ADK, no model, no
external assets, no JavaScript. Renders a CombinedReport as a single .html file:
the Layer 1 summary with each finding collapsible in place to its Layer 2 detail,
using native <details>/<summary>.

All model- and code-derived text is HTML-escaped (the audited script is untrusted
input), so a finding containing markup cannot break or inject into the page.
"""
from __future__ import annotations

from html import escape

from .layer2 import validate_suggestion
from .schema import CombinedReport, Finding

_CAVEAT = (
    "This tool reads code; it does not run it. Findings and fixes are reviewed "
    "proposals, not verified results \u2014 re-run any corrected script to confirm."
)

_SEV_CLS = {"Critical": "crit", "Important": "imp", "Minor": "min"}
_KIND_CLS = {"mechanical": "mech", "substantive": "subst"}
_KIND_LABEL = {
    "mechanical": "Mechanical fix \u2014 safe to apply after a check",
    "substantive": "Substantive fix \u2014 review the reasoning before accepting",
}

_CSS = """
*{box-sizing:border-box}
body{margin:0;background:#ffffff;color:#1a1d21;
 font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:920px;margin:0 auto;padding:0 20px 64px}
header.band{background:#23303a;color:#fff;padding:22px 0;margin-bottom:20px}
header.band .wrap{padding-bottom:0}
h1{font-size:20px;margin:0 0 4px;font-weight:650}
.sub{color:#c4ccd2;font-size:13px;margin:0;word-break:break-all}
.meta-row{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:12px;font-size:12.5px;color:#c4ccd2}
.counts{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0 8px}
.count{border-radius:999px;padding:4px 12px;font-size:12.5px;font-weight:600}
.count.crit{color:#b3261e;background:#fce8e6}
.count.imp{color:#8a5a00;background:#fef3d6}
.count.min{color:#5f6368;background:#eef0f2}
.notice{color:#5f6368;font-size:12.5px;background:#f6f7f9;border:1px solid #e3e6ea;
 border-radius:6px;padding:8px 12px;margin:8px 0 4px}
.sec-label{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#5f6368;
 margin:22px 0 8px;font-weight:600}
details.finding{border:1px solid #e3e6ea;border-radius:8px;margin:8px 0;background:#fff}
summary{list-style:none;cursor:pointer;padding:12px 14px;display:flex;gap:10px;align-items:baseline}
summary::-webkit-details-marker{display:none}
summary:focus-visible{outline:2px solid #4c8bf5;outline-offset:2px}
.badge{flex:none;font-size:11px;font-weight:700;text-transform:uppercase;padding:2px 8px;border-radius:4px}
.badge.crit{color:#b3261e;background:#fce8e6}
.badge.imp{color:#8a5a00;background:#fef3d6}
.badge.min{color:#5f6368;background:#eef0f2}
.s-title{font-weight:600}
.s-meta{color:#5f6368;font-size:12px;margin-left:auto;text-align:right}
.body{padding:2px 14px 14px;border-top:1px solid #e3e6ea}
.body h4{margin:12px 0 2px;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#5f6368}
.body p{margin:2px 0 8px}
.fix-kind{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;margin:6px 0}
.fix-kind.mech{color:#0b5cad;background:#e8f0fe}
.fix-kind.subst{color:#8a5a00;background:#fef3d6}
pre.diff{background:#f6f7f9;border:1px solid #e3e6ea;border-radius:6px;padding:10px 12px;overflow:auto;
 font:12.5px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;margin:4px 0}
pre.diff span{display:block;white-space:pre-wrap}
pre.diff .del{color:#b3261e}
pre.diff .add{color:#1e7d43}
.flag{color:#8a5a00;font-size:12.5px;margin:6px 0}
.clean{background:#e6f4ea;color:#1e7d43;border-radius:8px;padding:16px;font-weight:600}
footer{color:#5f6368;font-size:12px;margin-top:32px;border-top:1px solid #e3e6ea;padding-top:12px}
@media (max-width:560px){.s-meta{margin-left:0;text-align:left;width:100%}summary{flex-wrap:wrap}}
"""


def _esc(value) -> str:
    return escape(str(value if value is not None else ""), quote=True)


def _diff_html(suggestion: str) -> str:
    lines = (suggestion or "").splitlines()
    if not lines:
        return '<span>(no suggestion provided)</span>'
    out = []
    for line in lines:
        head = line.lstrip()
        cls = "del" if head.startswith("-") else "add" if head.startswith("+") else "ctx"
        out.append(f'<span class="{cls}">{_esc(line)}</span>')
    return "".join(out)


def render_finding(f: Finding) -> str:
    sev = _SEV_CLS.get(f.severity, "min")
    meta = " &middot; ".join(
        [_esc(f.area), _esc(f.location), _esc(f.rule_id), _esc(f.confidence)]
    )
    parts = [
        '<details class="finding">',
        '<summary>',
        f'<span class="badge {sev}">{_esc(f.severity)}</span>',
        f'<span class="s-title">{_esc(f.title)}</span>',
        f'<span class="s-meta">{meta}</span>',
        '</summary>',
        '<div class="body">',
        f'<h4>What</h4><p>{_esc(f.what)}</p>',
        f'<h4>Why it matters</h4><p>{_esc(f.why)}</p>',
        '<h4>Suggested fix</h4>',
        f'<div class="fix-kind {_KIND_CLS.get(f.fix_kind, "mech")}">'
        f'{_esc(_KIND_LABEL.get(f.fix_kind, f.fix_kind))}</div>',
        f'<pre class="diff">{_diff_html(f.suggestion)}</pre>',
    ]
    warn = validate_suggestion(f)
    if warn:
        parts.append(f'<p class="flag">[!] {_esc(warn)}</p>')
    parts.append('</div></details>')
    return "".join(parts)


def render_html(report: CombinedReport, source: str = "analysis script") -> str:
    c = report.counts
    n_total = sum(c.get(s, 0) for s in ("Critical", "Important", "Minor"))

    body = [
        '<div class="counts">',
        f'<span class="count crit">{c.get("Critical", 0)} Critical</span>',
        f'<span class="count imp">{c.get("Important", 0)} Important</span>',
        f'<span class="count min">{c.get("Minor", 0)} Minor</span>',
        '</div>',
        f'<div class="notice">{_esc(_CAVEAT)}</div>',
    ]

    if n_total == 0:
        body.append('<div class="clean">No issues found in the areas checked.</div>')
    else:
        for sev in ("Critical", "Important", "Minor"):
            group = [f for f in report.findings if f.severity == sev]
            if not group:
                continue
            body.append(f'<div class="sec-label">{sev} ({len(group)})</div>')
            body.extend(render_finding(f) for f in group)

    if report.scope_violations_dropped:
        body.append(
            f'<p class="flag">[!] {report.scope_violations_dropped} out-of-scope '
            f'finding(s) were dropped by the combiner.</p>'
        )

    analysis = _esc(", ".join(report.analysis_types) or "unclassified")
    checkers = _esc(", ".join(report.checkers_run))
    doc = [
        "<!DOCTYPE html>",
        '<html lang="en"><head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>Biomedical analysis audit \u2014 {_esc(source)}</title>",
        f"<style>{_CSS}</style>",
        "</head><body>",
        '<header class="band"><div class="wrap">',
        "<h1>Biomedical analysis audit</h1>",
        f'<p class="sub">{_esc(source)}</p>',
        '<div class="meta-row">'
        f"<span>Language: {_esc(report.language)}</span>"
        f"<span>Analysis: {analysis}</span>"
        f"<span>Checkers: {checkers}</span>"
        "</div>",
        "</div></header>",
        '<div class="wrap">',
        "".join(body),
        f"<footer>{_esc(_CAVEAT)}</footer>",
        "</div></body></html>",
    ]
    return "".join(doc)
