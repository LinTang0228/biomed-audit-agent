"""
Synthetic test fixture (CONTROL): clinical outcome prediction with a
leakage-free pipeline. Mock data. Expected to raise few or no issues; used to
measure the auditor's false-positive rate.
"""
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score

SEED = 42
rng = np.random.default_rng(SEED)

n = 500
X = pd.DataFrame(rng.normal(size=(n, 20)), columns=[f"f{i}" for i in range(20)])
groups = rng.integers(0, 120, size=n)          # patient identifier
y = (rng.random(n) < 0.3).astype(int)

# All learned preprocessing lives inside the pipeline, so it is fit within
# each training fold only.
pipe = Pipeline([
    ("scale", StandardScaler()),
    ("clf", LogisticRegression(max_iter=1000, random_state=SEED)),
])

# Group-aware, stratified cross-validation keeps each patient in one fold.
cv = StratifiedGroupKFold(n_splits=5)
scores = cross_val_score(pipe, X, y, groups=groups, cv=cv, scoring="roc_auc")

print(f"AUROC: {scores.mean():.3f} +/- {scores.std():.3f}")
