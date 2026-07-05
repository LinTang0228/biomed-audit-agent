# Biomedical Analysis Code Audit

An agent that reviews a single Python (`.py`) or R (`.R`) analysis script for the
mistakes that most often make biomedical results wrong or irreproducible, and
reports each one with a suggested fix. It reads code; it does not run it. It
advises; the researcher decides what to apply.

Built for the Kaggle *AI Agents: Intensive Vibe Coding* capstone (Agents for Good).

## Why an agent
Reviewing analysis code for statistical validity, study-design soundness, data
leakage, reproducibility, and honest interpretation requires judgement, tool use,
and the ability to drill from a summary into any single issue on demand. A single
prompt cannot do the layered, area-scoped, guideline-grounded review that a
routed set of specialist agents can.

## What it does
- **Input:** one analysis script (`.py` / `.R` / `.ipynb`).
- **Layer 1 (summary):** one line per finding, grouped by severity
  (Critical / Important / Minor) — compact enough to scan.
- **Layer 2 (drill-down):** for any finding, the full detail (What, Why) and a
  suggested fix shown as a before/after snippet, labelled **mechanical** (a single
  correct edit) or **substantive** (a scientific-content change to review).
- **Output:** a self-contained HTML report (Layer 1 with each finding collapsible
  to its Layer 2 detail), plus a structured JSON report.

## What it checks (six areas)
1. **Data handling** — inspection, missing values, outliers, derived variables,
   distribution-appropriate summaries.
2. **Study design** — independence of observations, confounding, biased selection.
3. **Statistics** — test choice, assumption checks, multiplicity, effect sizes and
   confidence intervals.
4. **Modelling & evaluation** — data leakage, metrics, validation (ML only).
5. **Reproducibility** — seeds, file paths, software versions, fragile constructs,
   secrets.
6. **Interpretation** — conclusions matching the evidence, causal language,
   selective reporting.

The rules are grounded in published standards (SAMPL, the EQUATOR reporting
guidelines, TRIPOD/TRIPOD+AI, and the ML-leakage literature).

## Architecture
```
script (.py / .R)
   |
   v
[triage]           deterministic: language + "is this an ML script?"  (routing)
   |
   v
[select checkers]  repro_coding + stats_design + interpretation  (+ leakage if ML)
   |
   v
[ParallelAgent]    the selected checkers run concurrently (ADK); each is an
   |               LlmAgent scoped to its area, grounded in the skill, writing
   |               structured findings to session.state
   v
[combine]          deterministic: enforce scope, de-duplicate, sort, count
   |
   v
Layer 1 summary  ->  Layer 2 drill-down  ->  HTML report
```
Design decisions: routing and combining are **deterministic Python** (one correct
answer, fully testable); the **model is reserved for the judgement-heavy checks**.

## Repository layout
```
biomed_audit_skill/        the skill (knowledge): SKILL.md + references/01..06
biomed_audit_system/       the system
  schema.py                findings + report data model
  triage.py                deterministic routing
  checkers.py              factory for the four scoped checker agents
  combiner.py              deterministic merge / scope / dedupe / sort
  orchestrator.py          triage -> ParallelAgent -> combine
  layer2.py                drill-down detail renderer
  html_report.py           self-contained HTML report
  run_audit.py             CLI: script -> summary (+ --json, --html)
  drilldown.py             CLI: report JSON -> Layer 2 detail
  render_report.py         CLI: report JSON -> HTML
  eval/                    answer_key.json, evaluate.py, run_all.py
fhs_fixtures/              R test scripts + GROUND_TRUTH_fhs.md
test_fixtures/             Python test scripts + GROUND_TRUTH.md
sample_report_*.html       example rendered reports
STAGE*_VERIFICATION.md     per-stage verification records
```

## Setup
```
pip install google-adk google-genai pydantic
export GOOGLE_API_KEY=...            # AI Studio key
export BIOAUDIT_MODEL=gemini-2.5-flash   # a model your key supports
export BIOAUDIT_SKILL_DIR=/path/to/biomed_audit_skill
```
Do not commit API keys.

## Usage
```
# audit one script -> summary + saved JSON + HTML report
python -m biomed_audit_system.run_audit fhs_fixtures/fhs_04_coding_bugs.R \
    --json report.json --html report.html

# drill into one finding (no model needed; uses the saved JSON)
python -m biomed_audit_system.drilldown report.json F1
python -m biomed_audit_system.drilldown report.json --severity Critical

# render HTML from a saved report (no model)
python -m biomed_audit_system.render_report report.json report.html

# evaluate against the ground truth (see below)
python -m biomed_audit_system.eval.run_all fhs_fixtures test_fixtures   # live run
python -m biomed_audit_system.eval.evaluate                            # deterministic scoring
```
The agent can also be developed and run in the Antigravity IDE / Agents CLI, and a
single checker can be explored in the ADK dev UI (`adk web`).

## Course concepts demonstrated
| Concept | Where | In this project |
|---|---|---|
| Multi-agent system (ADK) | Code | orchestrator runs a `ParallelAgent` of four scoped `LlmAgent` checkers, with deterministic routing and combining |
| Agent skills | Code | `biomed_audit_skill/` (SKILL.md + six reference files); each checker loads only its area's rules (progressive disclosure) |
| Antigravity | Video | the system is built and run in the Antigravity IDE / Agents CLI |

## Evaluation
`eval/answer_key.json` encodes the planted issues per fixture (from the fixtures'
ground-truth documents). `eval/run_all.py` runs the system over the fixtures and
saves each report; `eval/evaluate.py` scores those reports at rule-id granularity
and prints precision/recall (overall and by severity), severity agreement, and a
separate false-positive count on the clean control scripts.

## Verification status (honest)
Everything **deterministic** in this system has been executed and verified: the
skill's rule coverage (38/38 planted issues mapped) and no-false-positive check on
the controls; routing (correct on all 11 fixtures); the combiner (scope,
de-duplication, sorting, counts); the checker factory (each loads only its area's
rules); the Layer 2 renderer; and the HTML report (valid, self-contained, strict
escaping of untrusted content). Per-stage records are in `STAGE*_VERIFICATION.md`.

What is **not yet measured**: the checkers' live behaviour and the resulting
precision/recall. Those require a live Gemini run of the checkers, which the
development sandbox could not perform. The harness plus `answer_key.json` provide
the exact procedure to produce the numbers.

## Limitations
- Single-file, **static** review: no execution, no access to the data, no
  cross-file analysis. Many checks confirm a safeguard is *present in the code*,
  not that the *result is correct*.
- Suggested fixes are **reviewed proposals**, not verified results; re-run any
  corrected script to confirm.
- **R** deterministic depth is narrower than Python; judgement-based checks apply
  equally to both.
- Findings depend on a probabilistic model, so wording and borderline (Minor /
  judgement) findings vary between runs; Critical/Important items are the stable
  core. This tool assists, and does not replace, review by a qualified
  statistician.
