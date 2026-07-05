# Test Fixtures — Ground-Truth Answer Key

**Do not feed this file to the auditor.** It is the labeled reference used to
score the tool's output. These fixtures are synthetic and illustrative; the data
is mocked and the scripts are not meant to run to completion. Comments inside the
scripts are deliberately neutral so the tool must detect issues from code
structure, not from comments that name the flaw.

Severity uses the plan's scale: **Critical** (likely invalidates results now),
**Important** (could invalidate under realistic conditions, or breaks
reproducibility), **Minor** (risk/quality gap unlikely to change conclusions).

---

## test_01_ml_leakage.py — ML / clinical prediction

| # | Category | Severity | Location | Issue |
|---|----------|----------|----------|-------|
| 1 | Data leakage (preprocessing) | Critical | `scaler.fit_transform(X)` | Scaling fit on the full dataset before the split. |
| 2 | Data leakage (feature selection) | Critical | `SelectKBest(...).fit_transform` | Feature selection fit on the full dataset (and using `y`) before the split. |
| 3 | Data leakage (resampling) | Critical | `SMOTE().fit_resample` | Oversampling applied to the whole dataset before the split. |
| 4 | Data leakage (grouping) | Critical | `train_test_split(...)` | `patient_id` present but ignored; same patient can appear in train and test. |
| 5 | Evaluation metric | Important | `accuracy_score` | Accuracy as sole metric on a ~12% positive (imbalanced) target. |
| 6 | Reproducibility | Important | multiple | No global seed / `random_state` on `rng`, `train_test_split`, `SMOTE`, `RandomForestClassifier`. |

## test_02_omics_diffexp.py — Omics / differential expression

| # | Category | Severity | Location | Issue |
|---|----------|----------|----------|-------|
| 1 | Study design (confounding) | Critical | `batch` vs `condition` | Batch fully confounded with condition (b1=ctrl, b2=treat); biology and batch are inseparable. |
| 2 | Multiple comparisons | Critical | `pvals < 0.05` | 2000 per-gene tests thresholded at raw p<0.05 with no FDR/FWER correction. |
| 3 | Test appropriateness | Important | `stats.ttest_ind` | t-test on raw counts; no normalization or count-appropriate model. |
| 4 | Pseudoreplication | Important | `sample_id` | Two columns per biological sample (`sample_id` repeats) treated as independent replicates. |

## test_03_stats_comparison.py — Classical group comparison (+ security)

| # | Category | Severity | Location | Issue |
|---|----------|----------|----------|-------|
| 1 | Secret exposure | Important | `API_KEY = "sk-live-..."` | Hardcoded credential in source (security / secret-scan trigger). |
| 2 | Test appropriateness | Important | `stats.ttest_ind(group_a, group_b)` | Parametric t-test on small, skewed (exponential) samples with no normality check. |
| 3 | p-value interpretation | Important | `if p > 0.05: "No difference"` | Non-significance interpreted as evidence of equivalence. |
| 4 | Descriptive statistics | Minor | `stats.sem(...)` | SEM reported to describe sample spread instead of SD. |
| 5 | Multiple comparisons + selective reporting | Important | `for k in range(15)` | 15 secondary outcomes each tested at 0.05, no correction, only significant ones printed. |
| 6 | Causal language | Minor | final comment | Causal claim ("causes") drawn from an association. |

## test_04_survival.py — Survival analysis

| # | Category | Severity | Location | Issue |
|---|----------|----------|----------|-------|
| 1 | Immortal time bias | Critical | `df["treated"] = df["drug_start_day"].notna()` | Exposure defined from post-baseline information (drug started during follow-up). |
| 2 | Assumption check | Important | `cph.fit(...)` | Proportional-hazards assumption never assessed (no `check_assumptions`). |
| 3 | Reporting | Minor–Important | `print(... hr ...)` | Hazard ratio reported without a confidence interval. |
| 4 | Reproducibility | Minor | `pd.read_csv("/Users/lab/...")` | Hardcoded absolute local path; non-portable. |

## test_05_clean_control.py — CONTROL (expected clean)

Expected: **0 Critical, 0 Important.** At most one Minor (e.g., no dependency
pinning, or single model with no comparison). Any Critical/Important finding here
is a **false positive** and counts against precision. Rationale: preprocessing is
inside the `Pipeline` (fit per fold), CV is group-aware and stratified, the seed
is set, the metric (AUROC) suits the task, and variance is reported.

## test_06_diffexp.R — R differential expression

| # | Category | Severity | Location | Issue |
|---|----------|----------|----------|-------|
| 1 | Multiple comparisons | Critical | `which(pvals < 0.05)` | 2000 per-gene `t.test` at p<0.05 with no `p.adjust()`. |
| 2 | Reproducibility | Important | `sample(1:10, 6)` | `sample()` called with no `set.seed()`. |
| 3 | Robustness (R lint) | Minor | `done <- T` | `T` used instead of `TRUE` (can be reassigned). |

---

## Scoring protocol

For each script, run the auditor and match its findings to the rows above by
**category + location**. Then, per script and pooled across the set:

- **TP** = a ground-truth item the auditor reported.
- **FP** = an auditor finding with no matching ground-truth item (control-script
  Critical/Important findings are the primary FP source).
- **FN** = a ground-truth item the auditor missed.
- **Precision** = TP / (TP + FP); **Recall** = TP / (TP + FN).

Report precision/recall **per severity** and overall. For a rigor tool, weight
precision on the control script heavily — over-flagging erodes trust faster than
missing a Minor item. Treat borderline matches (right issue, wrong line;
right category, vague description) with a fixed rule (e.g., count as TP only if
location is within a few lines and the mechanism is named) and state that rule
in the writeup so the numbers are reproducible.

## Coverage of the set

| Analysis type | Fixture | Highest-value planted issue |
|---|---|---|
| ML / clinical prediction | 01 | Multi-form data leakage |
| Omics / differential expression | 02, 06 (R) | Batch confound; multiplicity |
| Classical group comparison | 03 | Multiplicity + test misuse (+ secret) |
| Survival | 04 | Immortal time bias |
| Control (clean) | 05 | — (false-positive test) |

Gaps you may want to add later: diagnostic-accuracy (STARD), a regression fixture
with low events-per-variable / multicollinearity, and a notebook (`.ipynb`)
version to exercise cell-order parsing.
