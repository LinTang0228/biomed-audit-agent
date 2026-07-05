# Stage 1 verification — the audit skill

Stage 1 delivers the knowledge base the tool checks against: `SKILL.md` (control
file) and six reference files (`references/01`–`06`). This document verifies its
**correctness** and **coverage** before any agent is built on it.

Three checks were run: (A) coverage — does every known issue in the test fixtures
map to a rule; (B) false positives — do the clean control scripts stay clean;
(C) statistical correctness and internal consistency.

---

## A. Coverage — every planted fixture issue maps to a rule

Fixtures live in `fhs_fixtures/` (R) and `test_fixtures/` (Python), with issues
listed in their `GROUND_TRUTH*` files. Each row below maps a planted issue to the
rule that should catch it.

**Framingham R fixtures**

| Fixture | Planted issue | Rule |
|---|---|---|
| fhs_02 | pooled t-test, equal-variance assumption unchecked (variances differ) | STAT-02 |
| fhs_02 | no distribution check (relies on large-n robustness unstated) | STAT-01 |
| fhs_02 | SEM used as the measure of spread | DATA-05 |
| fhs_02 | p-value only; no effect size or CI | STAT-04 |
| fhs_03 | age (confounder) not adjusted for | DESIGN-01 |
| fhs_03 | causal / clinical claim from observational data | INTERP-01 |
| fhs_03 | over-generalisation to patient advice | INTERP-04 |
| fhs_04 | silent, unjustified row filter (`SBP < 180`) | DATA-03 |
| fhs_04 | reversed `smoke` coding | DATA-07 |
| fhs_04 | wrong variable in model (`CIG`, not `smoke`) | DATA-08 |
| fhs_04 | stated conclusion contradicts the model | INTERP-02 |
| fhs_05 | absolute paths + `setwd()` | REPRO-02 |
| fhs_05 | unseeded `sample()` (also reduces n) | REPRO-01 (+ DATA-03) |
| fhs_05 | `T` / `F` literals | REPRO-04 |
| fhs_05 | ambiguous names; no `sessionInfo()` | REPRO-05 (+ REPRO-03) |

**Python fixtures**

| Fixture | Planted issue | Rule |
|---|---|---|
| test_01 | scaling fit before split | MODEL-01 |
| test_01 | feature selection fit before split | MODEL-01 |
| test_01 | SMOTE before split | MODEL-01 |
| test_01 | patient rows split across train/test | MODEL-02 |
| test_01 | accuracy on imbalanced target | MODEL-06 |
| test_01 | no seed / `random_state` | REPRO-01 |
| test_02 | batch confounded with condition | DESIGN-03 |
| test_02 | 2000 tests, no multiplicity correction | STAT-03 |
| test_02 | t-test on raw counts | STAT-01 |
| test_02 | pseudoreplication (`sample_id` repeats) | DESIGN-02 |
| test_03 | hardcoded secret | REPRO-06 |
| test_03 | parametric test on skewed data | STAT-01 |
| test_03 | p > 0.05 read as "no difference" | INTERP-03 |
| test_03 | SEM used as spread | DATA-05 |
| test_03 | 15 tests, no correction + only significant reported | STAT-03 + INTERP-06 |
| test_03 | causal claim from association | INTERP-01 |
| test_04 | immortal-time bias (post-baseline exposure) | DESIGN-04 |
| test_04 | proportional-hazards assumption untested | STAT-02 |
| test_04 | hazard ratio without CI | STAT-04 |
| test_04 | hardcoded absolute path | REPRO-02 |
| test_06 (R) | no `p.adjust()` | STAT-03 |
| test_06 (R) | no `set.seed()` | REPRO-01 |
| test_06 (R) | `T` instead of `TRUE` | REPRO-04 |

**Result: 38/38 planted issues map to a rule (100% coverage).** No fixture issue
is unaddressed by the skill.

## B. False positives — the clean control scripts stay clean

| Clean script | Rules that could fire | Verdict |
|---|---|---|
| `fhs_01_clean.R` | none of the Critical/Important rules — data inspected (DATA-01), missingness checked (DATA-02), recode verified (DATA-07), correct variable used (DATA-08), SD reported not SEM (DATA-05), variance tested and Welch used (STAT-02), effect sizes + CIs reported (STAT-04), age adjusted (DESIGN-01), associational language (INTERP-01), relative path (REPRO-02), `sessionInfo()` present (REPRO-03), `TRUE`/`FALSE` (REPRO-04). No randomness, so REPRO-01 is not applicable. | Clean. See borderline note below. |
| `test_05_clean_control.py` | preprocessing inside `Pipeline` (MODEL-01 satisfied), `StratifiedGroupKFold` with groups (MODEL-02), seed set (REPRO-01), AUROC metric (MODEL-06), fold variance reported (MODEL-07). | Clean. See borderline note below. |

**Borderline notes (honest calibration).** Two Minor findings are defensible on
the clean scripts and are within the "at most one Minor" tolerance stated in the
ground-truth files:
- `fhs_01_clean.R`: DATA-05 also concerns `mean ± SD` for skewed data. SBP is
  mildly right-skewed. The script reports SD (the correct measure of spread) and
  explicitly notes the skew and the large-n justification, so this should **not**
  fire; if a checker raises it, it is a Minor at most, not an error. This is a
  genuine judgement boundary and is the kind of case Stage 2 must be tuned on.
- `test_05_clean_control.py`: REPRO-03 (no pinned dependency file) could fire as a
  legitimate Minor. Acceptable.

No Critical or Important false positive is expected on either control.

## C. Statistical correctness and internal consistency

Key rules were cross-checked against authoritative standards and, where possible,
against the real FHS analysis (run in Python during fixture construction):
- **Welch vs pooled (STAT-02).** When group variances differ, Welch's t-test is
  appropriate; the pooled t-test and a simple linear model both assume equal
  variance (homoscedasticity). Confirmed on FHS: `var.test` F = 0.82, p = 0.011 →
  variances differ → Welch is correct. Grounding: standard statistical practice;
  SAMPL reporting guidance.
- **SEM vs SD (DATA-05).** SEM = SD/√n measures the precision of the mean, not the
  spread of the data. Grounding: SAMPL; widely documented misuse.
- **Multiplicity (STAT-03).** Many tests require FWER or FDR control. Grounding:
  Benjamini–Hochberg; standard in high-dimensional biology.
- **Leakage (MODEL-01/02).** Learned transforms must be fit on training data only;
  subjects must not span train and test. Grounding: the ML-reproducibility
  leakage literature (Kapoor & Narayanan).
- **Confounding / adjustment (DESIGN-01).** Confirmed on FHS: the smoke
  coefficient moves from −5.57 (crude) to −4.28 after adjusting for age; age is a
  strong predictor (p < 1e-9). The rule's logic matches the data.
- **Immortal-time bias (DESIGN-04), causal language (INTERP-01), "no effect"
  misread (INTERP-03).** Standard epidemiological and inferential principles.

Internal consistency: every rule carries a severity consistent with the SKILL.md
scale; every fixture severity in the ground-truth files is reproducible from the
rule definitions; the finding schema and the two-layer output format are fully
specified in SKILL.md.

## Limitations of this verification (important)
- This verifies the **rules** — their coverage, their statistical correctness, and
  their internal consistency **on paper**. It does **not** verify how a live
  agent, reading a script, will apply them. That behavioural check happens in
  Stage 2, when the first checker runs against these fixtures and its findings are
  compared to the ground truth.
- Coverage is demonstrated **against this fixture set**. Real-world scripts will
  contain issues not represented here; the skill is extensible but not exhaustive.
- Several rules (DESIGN-01/02/04, all of Area 6) require **judgement** and are not
  reducible to a syntactic pattern; their reliability depends on the model in
  Stage 2, not on this document.
- R deterministic depth is narrower than Python by design (see the reference
  files); this affects Stage 2 implementation, not the rules themselves.

## Conclusion
The skill covers every issue in the current fixtures, keeps the clean controls
clean (at most one defensible Minor each), and its statistical content checks out
against authoritative standards and the real FHS analysis. Stage 1 is sound as a
foundation. The next stage builds one checker against these fixtures and measures
its findings, which is where rule-correctness turns into measured behaviour.
