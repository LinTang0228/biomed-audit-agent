setwd("/Users/lin/Documents/BS723")
df <- read.csv("/Users/lin/Documents/BS723/fhs_2026Spring.csv")

# Work on a random subset for speed
df2 <- df[sample(nrow(df), 800), ]

df2$smoke <- ifelse(df2$CIG > 0, 1, 0)

tt  <- t.test(SBP ~ smoke, data = df2, var.equal = F)
tmp <- lm(SBP ~ smoke + Age, data = df2)
summary(tmp)

done <- T
