# Synthetic test fixture (R): differential expression across two conditions.
# Mock counts. For auditor evaluation only. Neutral comments by design.

counts <- matrix(rpois(2000 * 10, lambda = 40), nrow = 2000)   # genes x samples
condition <- c(rep("ctrl", 5), rep("treat", 5))

# Subsample columns for a quick check
idx <- sample(1:10, 6)
sub <- counts[, idx]

# Per-gene comparison
pvals <- apply(counts, 1, function(g) {
  t.test(g[condition == "ctrl"], g[condition == "treat"])$p.value
})

hits <- which(pvals < 0.05)
cat(length(hits), "genes with p < 0.05\n")

done <- T
