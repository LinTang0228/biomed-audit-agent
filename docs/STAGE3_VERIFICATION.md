# Stage 3 verification — the full system

Stage 3 assembles the router, the four checkers, and the deterministic combiner.
Unlike Stage 2, most of Stage 3's logic is deterministic and was therefore
**executed and verified in place**; only the checker LLM calls and the parallel
run require a live model.

## A. Verified here (executed)
1. **Syntax** — all modules under `biomed_audit_system/` compile.
2. **Routing — 11/11 fixtures correct.** `classify()` was run on every fixture.
   Language is correct in all cases; the ML gate (`run_leakage`) is `True` only for
   the two genuine ML scripts (`test_01`, `test_05`) and `False` for survival
   (`test_04`), omics (`test_02`), and every R classical-stats script. This is the
   only routing-critical decision and it is right everywhere.
3. **Combiner — verified on a constructed case** containing an out-of-scope
   finding, a duplicate, and mixed severities:
   - scope enforcement dropped exactly the 2 out-of-scope findings;
   - the duplicate `(rule_id, location)` was merged, keeping the most severe;
   - findings sorted Critical → Important → Minor;
   - counts correct; global ids `F1..Fn` assigned.
4. **Checker factory — verified for all four checkers.** Each loads only its own
   area's reference rules (no foreign rule-id prefixes appear in its rule text),
   exposes the correct `allowed_areas`, and uses the correct `output_key`.
5. **Layer 1 rendering** — produces the grouped summary format from `SKILL.md`.

## B. Expected end-to-end targets (scoring reference)
Derived by combining the per-checker ground truth. A correct run reproduces the
in-scope items and omits out-of-scope ones.

| Script | Checkers run | Expected findings |
|---|---|---|
| `fhs_02_stat_assumptions.R` | repro_coding, stats_design, interpretation | STAT-02, STAT-04 (stats); DATA-05 (repro_coding) |
| `fhs_03_confounding.R` | (same) | DESIGN-01 (stats); INTERP-01, INTERP-04 (interp) |
| `fhs_04_coding_bugs.R` | (same) | DATA-03, DATA-07, DATA-08 (repro_coding); INTERP-02 (interp); stats_design silent |
| `test_01_ml_leakage.py` | + leakage | MODEL-01 (×1–3), MODEL-02, MODEL-06 (leakage); REPRO-01 (repro_coding) |
| `test_04_survival.py` | repro_coding, stats_design, interpretation | DESIGN-04, STAT-02, STAT-04 (stats); REPRO-02 (repro_coding) |
| `fhs_01_clean.R` / `test_05_clean_control.py` | controls | 0 findings (≤1 defensible Minor) |

Note the cooperation patterns: `fhs_03` splits across `stats_design`
(missing adjustment) and `interpretation` (causal claim); `fhs_04`'s issues land
in `repro_coding` + `interpretation` while `stats_design` correctly stays silent;
`test_05` exercises the leakage checker returning clean.

## C. Not verified here (requires a live model)
- Each checker's actual findings on each script (the core behavioural measurement).
- The `ParallelAgent` run and the write/read of findings through `session.state`.
- Precision/recall and run-to-run variability.

## D. How to complete verification
1. Install dependencies; set the three environment variables.
2. `python -m biomed_audit_system.run_audit <fixture>` for each target in B.
3. Compare the combined Layer 1 output to B; record TP/FP/FN; compute precision
   and recall; note any out-of-scope finding that survived (a combiner or scope
   failure) and any missed target (watch `DESIGN-04` and multi-part `MODEL-01`).
4. Bring the numbers back. If adequate, Stage 4 (the fix step / Layer 2) follows;
   if not, we tune the checker instructions.

## Conclusion
Stage 3's deterministic backbone — routing, scope enforcement, merging, rendering
— is executed and correct. The system wires four scoped checkers into a routed,
parallel pipeline whose merge step is verifiable and verified. What remains is the
behavioural measurement of the checkers against a live model, with the target
table above as the yardstick.
