# Stage 3 — The full audit system

Router (manager) + four checkers + a deterministic combiner, producing the
Layer 1 summary from a single script.

## Architecture
```
script (.py / .R)
   │
   ▼
[triage]           deterministic: language + "is this an ML script?"   (Python, no model)
   │
   ▼
[select checkers]  repro_coding + stats_design + interpretation  (+ leakage only if ML)
   │
   ▼
[ParallelAgent]    the selected checkers run concurrently (ADK); each is an LlmAgent
   │               scoped to its area, grounded in the Stage 1 skill, writing its
   │               structured findings to session.state
   ▼
[combine]          deterministic: enforce scope, de-duplicate, sort, count   (Python, no model)
   │
   ▼
Layer 1 summary  +  findings JSON
```

Checker → area map: `stats_design` = study design + statistics; `repro_coding` =
data handling + reproducibility; `interpretation` = interpretation; `leakage` =
ML modelling/evaluation.

## Two deliberate design choices
- **The combiner is deterministic Python, not an agent.** Merging, scope
  enforcement, de-duplication, sorting, and counting have one correct answer;
  doing them in code removes model non-determinism from the merge and makes the
  step fully testable.
- **Routing is a deterministic classifier, not a model.** The only routing-
  critical decision is whether the script is ML (which gates the leakage checker).
  That is reliably detectable from imports/calls, so it is done with heuristics —
  which are also unit-testable without a live model. The model is reserved for the
  judgement-heavy checks themselves. Trade-off: the heuristics can misclassify
  unusual scripts; the analysis-type *tag* in the header is best-effort (e.g. a
  per-gene t-test loop is tagged "classical statistics", not "omics"), but this
  does not affect gating.

## Files
- `schema.py` — `Finding`, `AuditFindings` (per checker), `CombinedReport`.
- `triage.py` — deterministic language + ML detection (routing).
- `checkers.py` — factory that builds the four checker agents from the skill.
- `combiner.py` — deterministic merge/scope/dedupe/sort/count.
- `orchestrator.py` — triage → ParallelAgent of selected checkers → combine.
- `util.py` — line numbering, message building, Layer 1 rendering.
- `run_audit.py` — CLI entry point.

## Setup
As in Stage 2: install `google-adk`, `google-genai`, `pydantic`; set
`GOOGLE_API_KEY`, `BIOAUDIT_MODEL`, and `BIOAUDIT_SKILL_DIR` (path to the Stage 1
`biomed_audit_skill/`).

## Running it
Run as a module so the package imports resolve:
```
python -m biomed_audit_system.run_audit ../fhs_fixtures/fhs_04_coding_bugs.R
```
It prints the Layer 1 summary and the full `CombinedReport` JSON.

`adk web` runs a *single* agent, so it is best used on one checker at a time
(import a checker via `build_checker(name)`); the full pool is assembled
dynamically per script by the orchestrator and is exercised through
`run_audit`.

## Expected end-to-end behaviour (targets)
These combine the per-checker ground truth and are the scoring reference. They are
what a correct run should produce, not an observed run (the system was not
executed here — see the verification note). Critical/Important items are the
stable targets; Minor/judgement items may vary.

**`fhs_04_coding_bugs.R`** (checkers run: repro_coding, stats_design, interpretation)
- `repro_coding`: `DATA-03` (silent row filter), `DATA-07` (reversed `smoke`),
  `DATA-08` (wrong variable in model).
- `interpretation`: `INTERP-02` (conclusion contradicts the model).
- `stats_design`: **no findings** (this fixture's issues are outside its scope —
  a correct-silence check).
- Combined: ~4 findings; leakage checker not run.

**`test_01_ml_leakage.py`** (checkers run: all four, incl. leakage)
- `leakage`: `MODEL-01` (preprocessing before split — scaling, feature selection,
  SMOTE; may be 1–3 findings), `MODEL-02` (patient rows split across train/test),
  `MODEL-06` (accuracy on imbalanced target).
- `repro_coding`: `REPRO-01` (no seed / `random_state`).
- `stats_design`, `interpretation`: no findings.
- Combined: ~4–6 findings.

**`fhs_03_confounding.R`** — two checkers cooperate: `stats_design` → `DESIGN-01`
(no age adjustment); `interpretation` → `INTERP-01` (causal claim), `INTERP-04`
(over-generalisation).

**Controls** — `fhs_01_clean.R` and `test_05_clean_control.py` should yield **0**
findings (at most one defensible Minor); `test_05` also exercises the leakage
checker returning clean.

## Scoring and caveats
Score as in Stage 2 (TP/FP/FN vs the targets; precision/recall; out-of-scope
findings are scope failures). Caveats unchanged and important:
- **Not executed here.** No ADK runtime / API key / network in this environment,
  so the checkers and the parallel run were not exercised against a live model.
  Syntax, routing, the combiner, the factory, and rendering were verified
  deterministically (see `STAGE3_VERIFICATION.md`).
- **Model non-determinism** affects wording and Minor/judgement findings.
- **ADK version drift** may change `ParallelAgent` / `Runner` / session signatures;
  adjust to your installed version.
- **`output_schema` + parallel:** each checker writes structured output to its own
  `session.state` key; the combiner reads those. If a future checker needs tools,
  note that `output_schema` disables tool use in current ADK.
