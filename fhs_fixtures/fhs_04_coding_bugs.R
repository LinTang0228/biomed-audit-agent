# FHS Homework 10 - smoking status and SBP
fhs <- read.csv("fhs_2026Spring.csv")

# Restrict to a plausible BP range
fhs <- fhs[fhs$SBP < 180, ]

# Smoking status
fhs$smoke <- ifelse(fhs$CIG > 0, 0, 1)

# Regression of SBP on cigarette exposure
m <- lm(SBP ~ CIG, data = fhs)
summary(m)

# The coefficient is positive, so smokers have higher SBP than nonsmokers.
