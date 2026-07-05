# FHS R Fixtures - Ground-Truth Answer Key

**Do not feed this file to the auditor.** It is the labeled reference for
scoring. All scripts run the same homework analysis (Framingham subset,
n = 1406); each buggy script isolates one *category* of problem. Comments in the
buggy scripts are neutral by design, except where the flaw *is* an interpretive
claim (that claim is legitimately what the auditor should flag).

**Reference results** (verified in Python; confirm in R): smokers mean SBP 145.1
(SD 26.4, n = 633) vs nonsmokers 150.6 (SD 29.1, n = 773); var.test F = 0.82,
p = 0.011 (variances differ); Welch t = 3.76, p = 0.0002; simple regression
beta_smoke = -5.57, R^2 = 0.010; age-adjusted beta_smoke = -4.28 (p = 0.004),
beta_Age = 0.98 (p < 1e-9), R^2 = 0.037; adjusted mean SBP at mean age:
nonsmoker 150.0, smoker 145.8.

Severity: **Critical** (invalidates the stated conclusion), **Important** (could
change results/validity or breaks reproducibility), **Minor** (quality/robustness
gap). "Layer" indicates whether a deterministic static rule can catch it (Static)
or whether it needs semantic/domain judgment (LLM).

---

## fhs_01_clean.R - CONTROL (expected clean)

Expected auditor output: **0 Critical, 0 Important.** At most 1 Minor (e.g., "no
dependency pinning beyond sessionInfo"). Any Critical/Important finding here is a
**false positive**. Rationale: data inspected and completeness confirmed; recode
verified; SD (not SEM) reported; equal-variance assumption tested and Welch used
accordingly; effect sizes, CIs, test statistics, df, R^2 all reported;
confounding addressed by adjustment and model comparison; interpretation
associational, not causal; relative path; `sessionInfo()` recorded.

## fhs_02_stat_assumptions.R - Statistical assumptions & reporting

| # | Category | Severity | Layer | Location | Issue | Suggested fix |
|---|----------|----------|-------|----------|-------|---------------|
| 1 | Test assumption not checked | Important | LLM/Static | `t.test(..., var.equal = TRUE)` | Pooled (equal-variance) t-test used with no variance check; the assumption is violated here (F-test p = 0.011). | Run `var.test()` first; since variances differ, use Welch (the default `var.equal = FALSE`). |
| 2 | Distributional check omitted | Minor | LLM | whole script | No assessment of normality/skew of SBP (right-skewed); relies implicitly on large-n robustness without saying so. | Inspect the distribution; note CLT justification, or use a rank-based check as sensitivity. |
| 3 | Descriptive statistic misuse | Important | Static | `se_s`, `se_ns` (`sd/sqrt(n)`) | SEM reported as the measure of spread instead of SD. | Report SD (and/or median + IQR); reserve SEM/CI for precision of the mean, clearly labeled. |
| 4 | Incomplete reporting | Important | LLM/Static | `cat("p-value = ...")` | Only the p-value is reported: no effect size (mean difference), no 95% CI, no test statistic or df. | Report the estimate with 95% CI, the t statistic and df, alongside the exact p-value. |

## fhs_03_confounding.R - Confounding & causal interpretation

*The code is technically valid; the failures are in design and interpretation, so
a pure static linter would pass this. This is a good test of the semantic layer.*

| # | Category | Severity | Layer | Location | Issue | Suggested fix |
|---|----------|----------|-------|----------|-------|---------------|
| 1 | Uncontrolled confounding | Critical | LLM | `lm(SBP ~ smoke)` only | Never adjusts for age (or sex, cholesterol), despite the question being about confounding; reports the crude estimate as the effect. | Fit `SBP ~ smoke + Age` (consider further covariates); compare crude vs adjusted; discuss the change. |
| 2 | Causal overreach | Critical | LLM | closing comment ("smoking reduces...", "benefit of smoking") | Interventional/causal claims drawn from observational cross-sectional data. | Use associational language; note confounding and reverse-causation; make no interventional/clinical-advice claim. |
| 3 | Over-generalization | Minor | LLM | closing comment | Extends a within-sample association to patient advice without support. | Restrict claims to the observed association in this sample. |

## fhs_04_coding_bugs.R - Coding correctness & data handling

| # | Category | Severity | Layer | Location | Issue | Suggested fix |
|---|----------|----------|-------|----------|-------|---------------|
| 1 | Silent/unjustified exclusion | Important | Static/LLM | `fhs <- fhs[fhs$SBP < 180, ]` | Drops rows (changes n from 1406) with no justification or logging; 180 mmHg is a clinically meaningful value being discarded. | Justify and log any exclusion (report how many dropped); prefer the full cohort or a pre-specified rule; run a sensitivity analysis. |
| 2 | Reversed recode | Critical | LLM/Static | `ifelse(fhs$CIG > 0, 0, 1)` | Assigns 0 to smokers and 1 to nonsmokers - opposite of the specified "1 = smoker" - inverting the interpretation. | `ifelse(fhs$CIG > 0, 1, 0)`; verify with a `table()`. |
| 3 | Wrong variable in model | Critical | Static/LLM | `lm(SBP ~ CIG, ...)` | Fits continuous `CIG` (dose) instead of the binary `smoke` (status) the question asks about; the created `smoke` is never used. | Use `SBP ~ smoke`; if a dose-response is intended, state that explicitly and interpret per cigarette. |
| 4 | Consequent interpretation error | Important | LLM | closing comment | Claims "positive coefficient -> smokers higher SBP," which is wrong: the model uses CIG, not smoke, and smoke is reverse-coded. | Follows from fixing #2 and #3; re-interpret against the corrected model. |

## fhs_05_reproducibility.R - Reproducibility & hygiene

| # | Category | Severity | Layer | Location | Issue | Suggested fix |
|---|----------|----------|-------|----------|-------|---------------|
| 1 | Non-portable paths | Important | Static | `setwd(...)`, absolute `read.csv(...)` | User-specific absolute paths and `setwd()` break on any other machine. | Use a relative or project-relative path (e.g., `here::here()`); avoid `setwd()`. |
| 2 | Unseeded subsample | Important | Static/LLM | `df[sample(nrow(df), 800), ]` | `sample()` with no `set.seed()` -> non-reproducible; also arbitrarily reduces n from 1406 to 800, discarding data and power. | Set a seed if sampling is genuinely needed and justify it; otherwise analyze the full data. |
| 3 | `T`/`F` literals | Minor | Static | `var.equal = F`, `done <- T` | `T`/`F` can be reassigned as variables; a known R robustness pitfall. | Use `TRUE`/`FALSE`. |
| 4 | Readability / no environment record | Minor | Static/LLM | `df2`, `tmp`; no `sessionInfo()` | Ambiguous names and no package/version record hurt readability and reproducibility. | Descriptive names; record `sessionInfo()` or use `renv`. |

---

## Scoring
Match auditor findings to the rows above by **category + location**. Per script
and pooled: TP = ground-truth item reported; FP = reported item with no match
(the control script is the main FP source); FN = ground-truth item missed.
Precision = TP/(TP+FP); Recall = TP/(TP+FN). Report per severity; weight
precision on the control script heavily.

## Audit-dimension coverage
| Fixture | Primary dimension exercised | Detection layer stressed |
|---|---|---|
| 01 clean | (control) all dimensions, correctly done | false-positive rate |
| 02 | statistical rigor: assumptions + reporting | mixed |
| 03 | study design (confounding) + interpretation | semantic/LLM |
| 04 | coding correctness + data handling | mixed |
| 05 | reproducibility + computational hygiene | mostly static |

Gaps to add later: a multiplicity fixture (few tests here, so not central), an
interaction/effect-modification case (e.g., smoke x sex), and a notebook
(`.Rmd`/`.ipynb`) variant to exercise chunk-order parsing.
