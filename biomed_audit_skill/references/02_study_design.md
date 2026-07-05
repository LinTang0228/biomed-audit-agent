# Area 2 — Study design and data structure

Checks on whether the design supports the analysis: independence of observations,
control of confounding, and unbiased selection. These are frequently judgement
calls that need reading the code and metadata, not just pattern-matching.

---

**DESIGN-01 — Confounder not adjusted for**
- Look for: an exposure–outcome association reported crude, with a known common
  cause available in the data but omitted from the model (e.g. SBP on smoking
  without age, when age is present and relates to both).
- Why: omitting a confounder biases the estimated association; the crude estimate
  can overstate, understate, or reverse the adjusted one.
- Severity: Important (Critical when adjustment plausibly changes the conclusion,
  or when confounding is the explicit subject of the analysis).
- Fix (substantive): add the confounder(s) to the model; compare crude vs
  adjusted estimates and discuss the change. Note residual confounding remains
  possible.

**DESIGN-02 — Non-independent observations treated as independent**
- Look for: repeated measures per subject, multiple samples/cells per patient, or
  technical replicates entered as independent rows, then analysed with methods
  that assume independence (ordinary t-test, `lm`, `glm`). A signal is an
  ID/replicate column with duplicates that is ignored in the model.
- Why: pseudoreplication understates standard errors and inflates significance.
- Severity: Important (Critical when it drives the reported significance).
- Fix (substantive): model the clustering — a mixed-effects model
  (`lmer`/`glmer`, `statsmodels` mixed models), GEE, or cluster-robust standard
  errors — or aggregate to the independent unit.

**DESIGN-03 — Condition confounded with a technical/batch variable**
- Look for (omics/high-throughput especially): the biological variable of
  interest aligned with processing batch/run/lane/date (e.g. all cases in batch 1,
  all controls in batch 2), so biology and batch cannot be separated.
- Why: batch effects then masquerade as, or mask, the biological signal;
  normalisation alone does not fix a full confound.
- Severity: Critical.
- Fix (substantive): balance/randomise condition across batches by design; adjust
  for batch in the model or with an established correction, and check whether
  condition and batch are estimable separately.

**DESIGN-04 — Biased selection or exposure definition (incl. immortal-time bias)**
- Look for: exposure classified using information from *after* baseline
  (e.g. "treated" = received the drug at any point during follow-up), non-
  representative inclusion, or selection related to the outcome.
- Why: defining exposure with future information creates immortal-time bias;
  outcome-related selection biases estimates.
- Severity: Critical.
- Fix (substantive): define exposure using only baseline information, or use a
  time-varying exposure / landmark analysis; make inclusion representative of the
  target population.

**DESIGN-05 — Sample-size / power concern**
- Look for: a *post hoc* "observed power" computed from the result; or a null
  result interpreted as evidence of no effect in a visibly small sample.
- Report only when: there is a concrete signal in the script — a small sample is
  visible, or a non-significant result is read as "no effect." Do NOT raise the
  mere absence of an a-priori power statement as a finding: it is rarely
  expressible from code alone and is not, by itself, reportable.
- Why: underpowered studies yield unreliable estimates; post-hoc power is a
  deterministic function of the p-value and is uninformative.
- Severity: Minor.
- Fix (substantive): justify sample size a priori; do not report observed power —
  report the effect size with its confidence interval instead.
