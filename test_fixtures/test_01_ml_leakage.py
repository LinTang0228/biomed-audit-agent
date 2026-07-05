"""
Synthetic test fixture: clinical outcome prediction from tabular features.
Mock data; not a reference implementation. For auditor evaluation only.
Comments are intentionally neutral — the auditor must detect issues from the
code itself, not from comments that admit them.
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from imblearn.over_sampling import SMOTE

# Load data
n = 500
rng = np.random.default_rng()
X = pd.DataFrame(rng.normal(size=(n, 40)), columns=[f"feat_{i}" for i in range(40)])
patient_id = rng.integers(0, 120, size=n)      # patient identifier
y = (rng.random(n) < 0.12).astype(int)         # outcome label

# Standardize features
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Keep the top 10 features
selector = SelectKBest(f_classif, k=10)
X = selector.fit_transform(X, y)

# Balance the classes
X, y = SMOTE().fit_resample(X, y)

# Train / evaluate
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestClassifier()
model.fit(X_train, y_train)
pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, pred))
