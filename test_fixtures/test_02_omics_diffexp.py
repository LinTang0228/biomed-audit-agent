"""
Synthetic test fixture: differential expression between two conditions.
Mock count matrix. For auditor evaluation only. Neutral comments by design.
"""
import numpy as np
import pandas as pd
from scipy import stats

# Load counts: genes x samples
n_genes, n_samples = 2000, 12
rng = np.random.default_rng()
counts = pd.DataFrame(rng.poisson(50, size=(n_genes, n_samples)),
                      index=[f"g{i}" for i in range(n_genes)])

# Sample metadata
condition = np.array(["ctrl"] * 6 + ["treat"] * 6)
batch = np.array(["b1"] * 6 + ["b2"] * 6)
sample_id = np.array([1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6])   # two columns per sample

# Per-gene comparison
pvals = []
for g in counts.index:
    a = counts.loc[g, condition == "ctrl"]
    b = counts.loc[g, condition == "treat"]
    _, p = stats.ttest_ind(a, b)
    pvals.append(p)

pvals = np.array(pvals)
hits = counts.index[pvals < 0.05]
print(f"{len(hits)} differentially expressed genes")
