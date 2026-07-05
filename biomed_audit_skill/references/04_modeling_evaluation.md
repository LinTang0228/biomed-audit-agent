# Area 4 — Modelling and evaluation

Checks for machine-learning / predictive-modelling scripts. Skip these for a
script with no model fitting and evaluation. Data leakage is the highest-value
category here: it is common and it silently inflates reported performance.

---

**MODEL-01 — Preprocessing fit before the split (or outside CV folds)**
- Look for: any learned transform fit on the full data before `train_test_split`,
  or fit once outside a cross-validation loop: scaling/standardisation,
  imputation, feature selection, encoding, dimensionality reduction, and
  resampling such as SMOTE. Signals: `fit_transform(X)` on all rows before
  splitting; `SMOTE().fit_resample(X, y)` before splitting; `SelectKBest(...).fit`
  on all rows.
- Why: the transform sees test (or validation) data, leaking information and
  inflating performance estimates.
- Severity: Critical.
- Fix (mechanical → substantive): fit every learned transform on the training
  data only; put preprocessing inside a `Pipeline` so it is re-fit within each CV
  fold; resample only the training partition.

**MODEL-02 — Non-independent units split across train and test**
- Look for: rows that share a subject/patient/group assigned independently to
  train and test (a random row split when an ID column has duplicates); grouping
  ignored by `train_test_split` / plain `KFold`.
- Why: near-duplicate records on both sides let the model memorise subjects,
  inflating apparent generalisation.
- Severity: Critical.
- Fix (mechanical): split by group — `GroupKFold` / `StratifiedGroupKFold` /
  `GroupShuffleSplit`, passing the group/patient identifier.

**MODEL-03 — Temporal leakage**
- Look for: future information used to predict earlier outcomes; random (non-
  chronological) splitting of time-ordered data; features computed over a window
  that includes the prediction time.
- Why: the model exploits information unavailable at prediction time.
- Severity: Critical.
- Fix (substantive): split chronologically; compute features using only data
  available before the prediction point.

**MODEL-04 — Target leakage**
- Look for: a feature derived from, or a proxy for, the outcome, or one not
  available at the moment of prediction (e.g. a post-outcome measurement, a
  treatment assigned because of the outcome).
- Why: the model appears highly accurate by using information equivalent to the
  label.
- Severity: Critical.
- Fix (substantive): remove features not available at prediction time; construct
  the feature set from the prediction-time information only.

**MODEL-05 — Test set used for tuning or selection**
- Look for: hyperparameter tuning, threshold selection, or model choice performed
  on the same data reported as the test result; a single held-out set reused
  across many development rounds.
- Why: performance is optimistically biased by fitting to the test set.
- Severity: Important–Critical.
- Fix (substantive): use a separate validation split or nested cross-validation
  for tuning/selection; reserve the test set for a single final evaluation.

**MODEL-06 — Evaluation metric inappropriate for the task**
- Look for: accuracy as the sole metric on imbalanced classes; only a
  discrimination metric (AUROC) for a clinical risk model with no calibration; a
  metric that ignores the decision context.
- Why: accuracy is misleading under class imbalance; discrimination and
  calibration answer different questions.
- Severity: Important.
- Fix (mechanical → substantive): under imbalance report AUROC/AUPRC, balanced
  accuracy, F1, or MCC; for risk models report calibration alongside
  discrimination; choose metrics that match the intended use.

**MODEL-07 — Weak validation design**
- Look for: a single train/test split with no repetition; a point estimate of
  performance with no variance/interval across folds; no external validation where
  one is feasible and claimed.
- Why: a single split gives a high-variance, potentially unrepresentative estimate.
- Severity: Important.
- Fix (substantive): use (repeated) cross-validation and report variability;
  validate externally where the claim requires generalisation.
