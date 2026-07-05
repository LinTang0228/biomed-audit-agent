# Area 1 — Data handling

Checks on how the data is inspected, cleaned, and summarised before analysis.
Applies to essentially all scripts. Each check lists: what to look for, why it
matters, default severity, a detection hint, and a fix pattern.

---

**DATA-01 — Data not inspected before analysis**
- Look for: modelling/testing with no prior `str`/`summary`/`head`/`dim` (R) or
  `.info()`/`.describe()`/`.head()`/`.shape` (Python).
- Report only when: the absence of inspection connects to a concrete,
  script-specific risk — e.g. a variable is used in a way that suggests its type
  or coding may be wrong, or values feed a step sensitive to range or scale. Do
  NOT raise this as a generic hygiene reminder; a lack of inspection alone, with
  no visible downstream risk, is not reportable.
- Why: unexamined data hides type errors, impossible values, and structure that
  changes the correct analysis.
- Severity: Minor.
- Fix (mechanical): add a targeted inspection of the variables at risk.

**DATA-02 — Missing values handled questionably**
- Look for: the script explicitly acts on missing data in a questionable way —
  `na.omit()` / `dropna()` / `.fillna()` / imputation — with no report of how many
  rows were affected or why.
- Report only when: such handling is visible in the code. Do NOT raise this merely
  because no missingness check is present: whether missing values exist cannot be
  determined from the code alone (the data may have none), so the absence of a
  check is not, by itself, reportable, and ordinary `lm()`/`glm()` fitting is not a
  trigger.
- Why: listwise deletion or ad hoc imputation can bias results and silently change
  the sample; the missingness mechanism matters.
- Severity: Important.
- Fix (mechanical → substantive): quantify missingness
  (`colSums(is.na(x))` / `df.isna().sum()`); state and justify the handling.

**DATA-03 — Silent or unjustified row exclusion**
- Look for: filters that drop observations without justification or logging
  (e.g. `df[df$SBP < 180, ]`, `df = df[df.x < k]`), especially on a clinically
  meaningful threshold.
- Why: changes the sample and the result; undocumented exclusions are a common
  source of bias and non-reproducibility.
- Severity: Important (Critical if it plausibly drives the headline result).
- Fix (substantive): justify any exclusion, report the number of rows removed,
  prefer a pre-specified rule, and run a sensitivity analysis with/without it.

**DATA-04 — Outlier handling not justified**
- Look for: outlier removal/winsorising/clipping with no rationale or with an
  arbitrary cutoff.
- Why: ad hoc outlier removal is a researcher degree of freedom that can change
  conclusions.
- Severity: Important.
- Fix (substantive): pre-specify and justify; report sensitivity to the choice.

**DATA-05 — Summary statistic mismatched to the data (incl. SEM misuse)**
- Look for: (a) `mean ± SD` reported for clearly skewed data where median + IQR
  is more appropriate; (b) the **standard error of the mean** (`sd/sqrt(n)`,
  `sem()`, `std/np.sqrt(n)`) used to describe the **spread** of the data.
- Why: the SEM measures the precision of the mean estimate, not the variability
  of the observations; using it as spread understates dispersion. Skewed data are
  poorly summarised by mean ± SD.
- Severity: Minor–Important (Important when it is the reported measure of spread).
- Fix (mechanical): report **SD** (or median + IQR for skewed data) as the
  measure of spread; reserve SEM or a confidence interval for the precision of an
  estimate, clearly labelled.

**DATA-06 — Variable encoded with the wrong type**
- Look for: a categorical variable treated as continuous (or vice versa); an
  ordinal scale used as interval without comment; a factor's reference level left
  implicit where it affects interpretation.
- Why: the model and its interpretation depend on correct encoding.
- Severity: Important.
- Fix (mechanical → substantive): set the correct type (`factor()`,
  `astype('category')`); set an explicit, sensible reference level.

**DATA-07 — Derived / recoded variable defined incorrectly**
- Look for: a recode whose logic does not match the stated definition — wrong
  threshold, **reversed levels** (e.g. `ifelse(CIG > 0, 0, 1)` when 1 should mean
  smoker), or mislabelled categories.
- Why: a reversed or mis-thresholded variable inverts or distorts every downstream
  result and its interpretation.
- Severity: Critical.
- Fix (mechanical): correct the recode to match the definition; verify with a
  cross-tab (`table(raw, derived)`).

**DATA-08 — Variable used does not match the stated question**
- Look for: a variable is defined but never used, while a different variable is
  put in the model (e.g. a binary `smoke` is created but `lm(SBP ~ CIG)` uses the
  continuous dose); or the analysis silently answers a different question than the
  one posed.
- Why: the estimate no longer corresponds to the intended contrast.
- Severity: Critical.
- Fix (mechanical): use the intended variable; if a different specification is
  deliberate, state it and interpret it accordingly.
