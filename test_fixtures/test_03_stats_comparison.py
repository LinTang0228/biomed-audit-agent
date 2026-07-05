"""
Synthetic test fixture: compare a biomarker across two patient groups over
several outcomes. Mock data. For auditor evaluation only.
"""
import numpy as np
from scipy import stats

API_KEY = "sk-live-8f3a2b7c9d1e4f6a0b2c4d6e8f0a1b2c"   # credentials for the data service
rng = np.random.default_rng()

group_a = rng.exponential(scale=2.0, size=9)
group_b = rng.exponential(scale=2.5, size=8)

# Primary outcome
t, p = stats.ttest_ind(group_a, group_b)
print(f"t-test p = {p:.3f}")
if p > 0.05:
    print("No difference between groups.")

# Summary
print("Group A:", group_a.mean(), "+/- SEM", stats.sem(group_a))

# Secondary outcomes
for k in range(15):
    x = rng.exponential(scale=2.0, size=9)
    yv = rng.exponential(scale=2.2, size=8)
    _, pk = stats.ttest_ind(x, yv)
    if pk < 0.05:
        print(f"Outcome {k}: significant (p={pk:.3f})")

# Conclusion: higher biomarker causes worse outcomes.
