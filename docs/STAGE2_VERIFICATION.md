# Stage 2 verification — statistics & study-design checker

Stage 2 delivers one checker as an ADK agent plus a runner. Because this
environment has no ADK runtime, no API key, and restricted network, the agent was
**not executed against a live model**. This document states exactly what *was*
verified, what was *not*, and how you complete the verification in your
environment.

## A. What was verified here (static)
1. **Syntax.** `agent.py`, `__init__.py`, and `run_checker.py` all compile
   (`python -m py_compile`).
2. **Skill rules load.** The agent reads Area 2 and Area 3 from the Stage 1 skill:
   `02_study_design.md` (5 DESIGN rules) and `03_statistics.md` (6 STAT rules)
   load and contain the expected rule ids.
3. **Output formatter.** `number_lines` prefixes lines correctly, and
   `print_summary` renders the Layer 1 format from `SKILL.md`, sorted
   Critical → Important → Minor. Verified on a mock findings object.
4. **Schema conformance.** `Finding` / `AuditFindings` match the finding schema in
   `SKILL.md` (fields, severities, `fix_kind`, `confidence`).
5. **Scope design.** The instruction restricts the checker to DESIGN-* and STAT-*
   and explicitly forbids reporting other areas. The expected-output targets below
   encode this: each in-scope target is listed, and each out-of-scope item that
   must **not** appear is named.
6. **ADK-pattern conformance.** The agent uses the documented `LlmAgent` +
   `output_schema` + `output_key` pattern; the runner uses the documented
   `Runner` + session-service + `run_async` event loop. (Exact signatures may
   still differ by ADK version — see limitations.)

## B. Expected-output targets (the scoring reference)
Derived from the fixtures' ground truth and the Stage 1 rules. A correct run
should reproduce the in-scope items and omit the out-of-scope ones.

| Script | In-scope targets | Must NOT appear (out of scope) |
|---|---|---|
| `fhs_02_stat_assumptions.R` | STAT-02 (Imp), STAT-04 (Imp), STAT-01 (Minor, optional) | DATA-05 (SEM) |
| `fhs_03_confounding.R` | DESIGN-01 (Imp–Crit) | INTERP-01, INTERP-04 |
| `test_04_survival.py` | DESIGN-04 (Crit), STAT-02 (Imp), STAT-04 (Minor–Imp) | REPRO-02 |
| `test_02_omics_diffexp.py` | DESIGN-03 (Crit), DESIGN-02 (Imp), STAT-03 (Crit), STAT-01 (Imp) | — |
| `fhs_01_clean.R` (control) | none | any Critical/Important finding |

Note: `DESIGN-04` (immortal-time bias) is the judgement-heaviest detection and the
most likely false negative; `fhs_04`'s issues are all out of scope for this
checker (data-handling / interpretation) and should produce **no** findings here.

## C. What was NOT verified (requires your run)
- **Live model behaviour** — whether the agent, reading each script, actually
  produces the targets above. This is the core measurement and cannot be done
  without a live Gemini model.
- **Precision / recall numbers** — computed by comparing an actual run to
  section B.
- **Non-determinism spread** — how much repeated runs vary (run each target 2–3
  times; expect Minor/judgement items to move, Critical/Important to be stable).

## D. How to complete the verification
1. Install dependencies; set `GOOGLE_API_KEY`, `BIOAUDIT_MODEL`, and
   `BIOAUDIT_SKILL_DIR` (see `STAGE2_README.md`).
2. Run each target script with `python run_checker.py <path>` (or `adk web`).
3. For each script, mark TP / FP / FN against section B; compute precision and
   recall; note any out-of-scope finding (a scope failure) and any missed
   in-scope target (especially `DESIGN-04`).
4. Bring the numbers back. If precision/recall are adequate, we proceed to
   Stage 3 (manager + the other checkers + combiner). If not, we iterate on the
   instruction first — the likely dials are the scope paragraph (to cut
   out-of-scope FPs) and the phrasing of the judgement rules (to cut FNs).

## Conclusion
Everything checkable without a model passes: the code compiles, the skill rules
load, the schema and formatter are correct, and the scope is well defined with
explicit targets. What remains is the behavioural measurement, which is yours to
run — the expected-output table is the yardstick. This is the point where
rule-correctness (Stage 1) becomes measured agent behaviour.
