# Stage 5 - The HTML report

A single self-contained `.html` file rendered deterministically from a
`CombinedReport`: the Layer 1 summary with each finding collapsible in place to
its Layer 2 detail. No model, no server, no JavaScript, no external assets.

## What it produces
- A slate header with the source, language, analysis types, and checkers run.
- A severity count bar (Critical / Important / Minor) and a one-line notice of the
  read-not-run limitation.
- Findings grouped by severity; each is a native `<details>` card whose summary is
  the Layer 1 line (severity badge, title, area, location, rule id, confidence) and
  whose body is the Layer 2 detail (What, Why, the suggested fix with a
  mechanical/substantive label and a diff-coloured before/after, and any
  validation flag).
- A clean state ("No issues found in the areas checked.") when there are no
  findings.

## Design choices (and why)
- **Restraint over decoration.** A neutral white report with a slate header and
  semantic severity colours (red / amber / grey), deliberately avoiding the
  AI-default cream/serif/terracotta look. Colour and grouping encode severity -
  real information - rather than ornament. This is the appropriate register for a
  supervisor-facing technical report.
- **Native `<details>` for drill-down.** Collapsible detail with no JavaScript, so
  the file renders identically offline and cannot execute anything.
- **System font stack + monospace for code.** Legibility and neutrality suit the
  subject; no web-font downloads keeps the file self-contained.
- **Accessibility floor.** Visible keyboard focus on each summary; responsive down
  to mobile.

## Files
- `html_report.py` - `render_html(report, source)` and the finding renderer.
- `render_report.py` - CLI: report JSON in, HTML file out.

## Usage
1. Produce and save a report JSON:
   ```
   python -m biomed_audit_system.run_audit ../fhs_fixtures/fhs_04_coding_bugs.R
   # copy the printed JSON into report.json
   ```
2. Render the HTML:
   ```
   python -m biomed_audit_system.render_report report.json report.html "fhs_04_coding_bugs.R"
   ```

Two ready-made examples are included: `sample_report_fhs04.html` (four findings
across two checkers) and `sample_report_clean.html` (the clean state).

## Escaping (correctness and safety)
All model- and code-derived text - titles, `what`, `why`, suggestions, locations -
is HTML-escaped with `html.escape(..., quote=True)`. The audited script is
untrusted input, so a finding that contains markup (or a script's comment that
contains `<script>`) is rendered as inert text and cannot break the page or inject
into it. This is verified against a hostile-content report in
`STAGE5_VERIFICATION.md`.

## Boundary
Stage 5 is deterministic and fully verified here. Like Stages 4, it presents
whatever the report contains; whether the findings and fixes are good depends on
the checkers (Stages 2-3), whose live behaviour is still to be measured.
