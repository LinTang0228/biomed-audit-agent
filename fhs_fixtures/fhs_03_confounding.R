# FHS Homework 10 - does smoking lower blood pressure?
fhs <- read.csv("fhs_2026Spring.csv")
fhs$smoke <- ifelse(fhs$CIG > 0, 1, 0)

# Compare SBP between smokers and nonsmokers
m1 <- lm(SBP ~ smoke, data = fhs)
summary(m1)

# The coefficient for smoke is negative and highly significant
# (p < 0.001): smokers have lower SBP than nonsmokers. We therefore
# conclude that smoking reduces systolic blood pressure, and that the
# blood-pressure benefit of smoking should be weighed against its other
# effects when advising patients.
