# Area 3 — Statistics

Checks on inferential method: choosing the right test, checking its assumptions,
correcting for multiple testing, and reporting effect sizes with confidence
intervals. (Descriptive-statistic issues are in Area 1; conclusions drawn from
results are in Area 6.)

---

**STAT-01 — Test inappropriate for the data type or distribution**
- Look for: a parametric test on small and/or clearly skewed data with no check
  (t-test/ANOVA on skewed outcomes; small groups); a t-test/linear model applied
  to raw count data; a continuous method on categorical data.
- Why: violated distributional assumptions distort p-values and intervals,
  especially at small n.
- Severity: Important.
- Fix (substantive): use a method matched to the data — a rank-based test
  (Wilcoxon/Kruskal–Wallis), an exact test, or a count model (Poisson/negative
  binomial); or justify robustness (e.g. large n via the central limit theorem).

**STAT-02 — Test assumption not checked or violated**
- Look for: an assumption the chosen method requires, neither checked nor met.
  Common cases: **equal variance** for a pooled two-sample t-test
  (`var.equal = TRUE`, `equal_var=True`) with no variance check — when variances
  differ, Welch's t-test is appropriate and is the safer default; **proportional
  hazards** for a Cox model, never tested; **linearity / residual** diagnostics
  for linear regression, absent.
- Why: inference is only valid if the assumptions hold; the equal-variance pooled
  t-test and a linear model both assume homoscedasticity, which Welch's test does
  not.
- Severity: Important.
- Fix (mechanical → substantive): test the assumption (`var.test`/Levene;
  `cox.zph` / `check_assumptions`; residual plots) and use a method consistent
  with the result (e.g. Welch's t-test — `t.test(...)` default,
  `equal_var=False`; stratified/time-varying Cox).

**STAT-03 — Multiple comparisons not corrected**
- Look for: many hypothesis tests (a loop over genes/outcomes; several endpoints)
  each judged at α = 0.05, with no family-wise or false-discovery-rate control;
  absence of `p.adjust()` / `multipletests()` where many p-values are produced.
- Why: without correction the expected number of false positives grows with the
  number of tests.
- Severity: Critical in high-dimensional settings (e.g. omics); Important for a
  handful of endpoints.
- Fix (mechanical → substantive): control FWER (Bonferroni/Holm) or, more
  commonly for many tests, FDR (Benjamini–Hochberg; Benjamini–Yekutieli or
  Storey q-values under dependence) at the correct family scope.

**STAT-04 — Effect size and/or confidence interval not reported**
- Look for: the script's reported output is limited to a p-value or a
  "significant/not" verdict with no accompanying estimate; or an odds ratio,
  relative risk, hazard ratio, or coefficient is presented as a bare point value
  with no interval.
- Report only when: an inferential result is actually reported and lacks any
  effect size or interval. Do NOT raise this when the script calls a summary that
  already reports standard errors or intervals (e.g. R's `summary()` on an
  `lm`/`glm`, `confint()`, or a `statsmodels` `.summary()`), since the interval is
  then available in the output; and do not raise it when an effect size or CI is
  already present.
- Why: statistical significance says nothing about magnitude or precision; the
  effect size with its interval is what supports interpretation.
- Severity: Important.
- Fix (mechanical): report the estimate (difference in means, coefficient, OR/RR/
  HR) with a 95% confidence interval, alongside the test statistic, degrees of
  freedom, and the exact p-value.

**STAT-05 — Too many predictors for the available information (overfitting)**
- Look for: a regression with many predictors relative to sample size or event
  count; automated stepwise selection presented as a final model.
- Why: too few events per predictor gives unstable, optimistic estimates; stepwise
  selection biases coefficients and p-values.
- Severity: Important (context-dependent).
- Fix (substantive): a common rule of thumb is roughly ≥ 10 events per predictor
  (a guideline, not a law); pre-specify predictors or use penalised regression;
  avoid presenting stepwise output as if pre-specified.

**STAT-06 — Multicollinearity unexamined in a multivariable model**
- Look for: several strongly related predictors entered together with no
  collinearity check.
- Why: collinearity inflates standard errors and destabilises coefficients,
  complicating interpretation.
- Severity: Minor–Important.
- Fix (mechanical): check variance inflation factors (`vif`); consider combining
  or dropping redundant predictors.
