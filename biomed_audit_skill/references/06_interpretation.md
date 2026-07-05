# Area 6 — Interpretation and reporting

Checks on whether the stated conclusions are supported by what the analysis
actually did. These are judgement-based and usually live in comments, printed
messages, or write-up text rather than in the computation itself.

---

**INTERP-01 — Causal language from non-experimental data**
- Look for: causal or interventional wording ("X reduces/causes/prevents Y",
  "the effect of X", policy or treatment advice) drawn from observational or
  purely correlational analysis.
- Why: association does not establish causation; observational estimates carry
  confounding and, in cross-sectional data, no established temporality.
- Severity: Critical when the causal claim is the headline; Important otherwise.
- Fix (substantive): use associational wording ("is associated with"); state
  confounding and reverse-causation as limitations; make no interventional claim
  the design cannot support.

**INTERP-02 — Conclusion contradicts or overstates the analysis**
- Look for: a stated conclusion inconsistent with the model actually fit (wrong
  variable, wrong sign owing to a reversed code, a claim about a contrast not
  estimated); a conclusion stronger than the estimate and its uncertainty support.
- Why: the reader is told something the analysis does not show.
- Severity: Critical (wrong) or Important (overstated).
- Fix (substantive): align the conclusion with the estimate, its direction, and
  its confidence interval; correct the underlying code issue first if there is one.

**INTERP-03 — Non-significant result read as "no effect"**
- Look for: p > 0.05 interpreted as "no difference", "groups are equivalent", or
  "no association".
- Why: absence of evidence is not evidence of absence; a non-significant result is
  consistent with a range of effects, including meaningful ones.
- Severity: Important.
- Fix (substantive): report the estimate and confidence interval and describe what
  effects remain plausible; use an equivalence test if equivalence is the claim.

**INTERP-04 — Over-generalisation beyond the sample studied**
- Look for: conclusions extended to populations, settings, or exposures not
  represented in the data.
- Why: external validity is not guaranteed by an in-sample result.
- Severity: Minor–Important.
- Fix (substantive): restrict claims to the studied sample/population, or justify
  transportability explicitly.

**INTERP-05 — Statistical significance conflated with practical importance**
- Look for: a small effect described as important solely because p is small,
  especially at large n; magnitude not discussed.
- Why: with large samples, trivial effects reach significance; significance does
  not imply clinical or practical relevance.
- Severity: Minor–Important.
- Fix (substantive): interpret the effect size against a domain-relevant
  threshold, not the p-value alone.

**INTERP-06 — Selective reporting**
- Look for: many analyses or outcomes computed but only the significant or
  favourable ones reported; a subgroup or model chosen after seeing results and
  presented as primary.
- Why: reporting only favourable results biases the evidence and inflates false
  positives.
- Severity: Important.
- Fix (substantive): report all pre-specified analyses and outcomes; label
  post-hoc/exploratory analyses as such.
