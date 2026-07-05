# =====================================================================
# FHS Homework 10 - Smoking status and systolic blood pressure (SBP)
# Rigorous REFERENCE implementation (base R). Expected to raise no
# material issues; used as the clean control for the auditor.
#
# Question: Is smoking status associated with SBP, and is any crude
# association confounded by age?
# Data: Framingham Heart Study subset (n = 1406). Observational cohort
# data -> associations are not causal.
# Analysis logic verified numerically in Python; run once in R to confirm.
# =====================================================================

## ---- 0. Load and inspect -------------------------------------------
fhs <- read.csv("fhs_2026Spring.csv", stringsAsFactors = FALSE)

str(fhs)
summary(fhs)
colSums(is.na(fhs))                      # confirm completeness
table(fhs$Sex)                           # confirm coding: MALE / FEM
sapply(fhs[c("SBP", "Age", "CIG")],
       function(x) c(min = min(x), max = max(x)))

## ---- 1. Define exposure --------------------------------------------
# smoke = 1 if any cigarettes/day (CIG > 0), else 0 (per assignment).
fhs$smoke <- as.integer(fhs$CIG > 0)
table(CIG_positive = fhs$CIG > 0, smoke = fhs$smoke)   # verify recode
addmargins(table(fhs$smoke))

## ---- 2. Descriptives by group (mean and SD, not SEM) ---------------
# SBP is right-skewed; with n this large the t-test is robust, but we
# report SD as the measure of spread and inspect the distribution.
aggregate(SBP ~ smoke, data = fhs,
          FUN = function(x) c(n = length(x), mean = mean(x), sd = sd(x)))
# Optional visual checks (skew / outliers), left commented:
# hist(fhs$SBP); boxplot(SBP ~ smoke, data = fhs)

## ---- 3. Two-sample t-test (Q1) -------------------------------------
# Assumption check first: equality of variances (F-test).
#   H0: var_smoker = var_nonsmoker ;  H1: not equal.
vt <- var.test(SBP ~ smoke, data = fhs)
print(vt)                                # F ~ 0.82, p ~ 0.011 -> differ

# The equal-variance assumption is rejected, so Welch's t-test is the
# appropriate primary analysis (var.equal = FALSE is the default).
#   H0: mu_smoker = mu_nonsmoker ;  H1: mu_smoker != mu_nonsmoker.
tt_welch  <- t.test(SBP ~ smoke, data = fhs)               # Welch (primary)
print(tt_welch)
tt_pooled <- t.test(SBP ~ smoke, data = fhs, var.equal = TRUE)  # for Q2 link
print(tt_pooled)

# Effect size = difference in group means (t.test also returns a 95% CI).
means <- tapply(fhs$SBP, fhs$smoke, mean)
cat("Mean SBP difference (smoker - nonsmoker):",
    round(means["1"] - means["0"], 2), "mmHg\n")

## ---- 4. Simple linear regression (Q2) ------------------------------
#   H0: beta_smoke = 0 ;  H1: beta_smoke != 0.
m1 <- lm(SBP ~ smoke, data = fhs)
summary(m1)                              # beta, SE, t, df, p, R^2
confint(m1)                              # 95% CI for beta_smoke
# beta_smoke equals the pooled-variance mean difference, so the simple
# regression corresponds to the POOLED t-test: same |t| and p-value (the
# sign differs only because of which group is the reference). Regression
# assumes homoscedasticity; Welch's t-test does not.

## ---- 5. Multiple linear regression, adjusting for age (Q3) ---------
m2 <- lm(SBP ~ smoke + Age, data = fhs)
summary(m2)                              # global F, R^2, coefficients
confint(m2)

# Adjusted mean SBP for smokers and nonsmokers at the sample mean age.
adj <- predict(m2, newdata = data.frame(smoke = c(0, 1),
                                        Age = mean(fhs$Age)))
names(adj) <- c("nonsmoker", "smoker")
print(round(adj, 2))

## ---- 6. Model comparison and interpretation ------------------------
# Crude beta_smoke (m1) ~ -5.6 mmHg; age-adjusted (m2) ~ -4.3 mmHg. Age
# is positively associated with SBP and smokers are slightly younger, so
# age partly confounds the crude association: adjustment attenuates it
# (~23%) toward the null, though an inverse association remains.
# The age-adjusted model is preferred here: it removes confounding by a
# strong predictor (age), raises R^2 (~0.010 -> ~0.037), and gives a less
# biased estimate. Interpretation is associational, not causal
# (residual confounding by sex, cholesterol, etc. is plausible).

## ---- 7. Reproducibility --------------------------------------------
sessionInfo()
