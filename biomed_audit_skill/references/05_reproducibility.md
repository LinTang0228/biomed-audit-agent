# Area 5 — Reproducibility and computational hygiene

Checks on whether someone else (or the author later) could re-run the script and
obtain the same result. Most of these are pattern-based and apply to both
languages; language-specific notes are marked.

---

**REPRO-01 — Random seed not set for stochastic steps**
- Look for: any randomness — resampling, random splits, stochastic model fitting,
  bootstrap, simulation — with no seed. R: `sample()`/random draws with no
  `set.seed()`. Python: `train_test_split`, samplers, or estimators with no
  `random_state`, and `numpy`/`random` unseeded.
- Why: results (splits, estimates, figures) change between runs and cannot be
  reproduced.
- Severity: Important.
- Fix (mechanical): set a fixed seed once (`set.seed(...)`) and pass
  `random_state=` to every stochastic function.

**REPRO-02 — Non-portable file paths**
- Look for: absolute or user-specific paths (`/Users/...`, `C:\\...`,
  `/home/<name>/...`); `setwd()` to a machine-specific directory.
- Why: the script breaks on any other machine, defeating reproducibility.
- Severity: Important.
- Fix (mechanical): use relative or project-relative paths (R: `here::here()`;
  Python: paths relative to the script/project); avoid `setwd()`.

**REPRO-03 — Software and package versions not recorded**
- Look for: no `sessionInfo()` (R) / no `requirements.txt`, `environment.yml`,
  `renv.lock`, or printed versions.
- Report only when: the script depends on third-party packages whose behaviour can
  differ across versions (e.g. statistical, ML, or bioinformatics libraries), so
  that the missing version record is a concrete reproducibility risk. Do NOT raise
  it for base-language scripts with no such dependencies, or as a generic reminder.
  Raise at most once per script, at the lowest priority.
- Why: analyses can change across package versions; without a version record the
  environment cannot be reconstructed.
- Severity: Minor.
- Fix (mechanical): record `sessionInfo()` or pin dependencies (`renv`,
  `requirements.txt`).

**REPRO-04 — Fragile language constructs**
- Look for (R): `T` / `F` used for `TRUE` / `FALSE`.
- Why: `T` and `F` are ordinary variables that can be reassigned, silently
  changing behaviour; `TRUE`/`FALSE` are reserved and safe.
- Severity: Minor.
- Fix (mechanical): use `TRUE` / `FALSE`.

**REPRO-05 — Silent data mutation or unclear naming**
- Look for: overwriting the raw data object in place through several steps;
  uninformative names (`df2`, `tmp`, `x`) that obscure what is being analysed.
- Why: reduces readability and makes the transformation history hard to audit or
  reproduce.
- Severity: Minor.
- Fix (mechanical): keep the raw data immutable; use descriptive, versioned names
  for derived objects.

**REPRO-06 — Hardcoded secret in source**
- Look for: an API key, password, or token assigned as a literal
  (e.g. `API_KEY = "sk-..."`).
- Why: committing a secret to code is a security exposure; it also ties the script
  to a private credential.
- Severity: Important.
- Fix (mechanical): load secrets from an environment variable or a secrets manager;
  remove the literal and rotate the exposed credential.
- Reporting rule: flag the location, but do **not** reproduce the secret value.
