# FHS Homework 10 - smoking status and SBP.
fhs <- read.csv("fhs_2026Spring.csv")
fhs$smoke <- ifelse(fhs$CIG > 0, 1, 0)

# Group summaries
n_s  <- sum(fhs$smoke == 1); n_ns <- sum(fhs$smoke == 0)
m_s  <- mean(fhs$SBP[fhs$smoke == 1])
m_ns <- mean(fhs$SBP[fhs$smoke == 0])
se_s  <- sd(fhs$SBP[fhs$smoke == 1]) / sqrt(n_s)
se_ns <- sd(fhs$SBP[fhs$smoke == 0]) / sqrt(n_ns)
cat("Smokers SBP:   ", round(m_s, 1),  "+/-", round(se_s, 2),  "\n")
cat("Nonsmokers SBP:", round(m_ns, 1), "+/-", round(se_ns, 2), "\n")

# Two-sample t-test
tt <- t.test(SBP ~ smoke, data = fhs, var.equal = TRUE)
cat("p-value =", round(tt$p.value, 4), "\n")
if (tt$p.value < 0.05) {
  cat("Smoking status is significantly associated with SBP.\n")
}
