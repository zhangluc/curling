# adds Has_Hammer column to Stones.csv (0 = no hammer, 1 = has hammer)

library(readr)
library(dplyr)

# Load Stones.csv
stones <- read_csv("dfs/Stones.csv")

# Step 1: Identify hammer team per end
# In mixed doubles, stones 7–12 are thrown by the hammer team
hammer_by_end <- stones %>%
  filter(ShotID >= 7) %>%   # hammer team shots
  group_by(CompetitionID, SessionID, GameID, EndID) %>%
  summarise(
    Hammer_TeamID = first(TeamID),
    .groups = "drop"
  )

# Step 2: Join hammer info back to FULL stones data
stones_with_hammer <- stones %>%
  left_join(
    hammer_by_end,
    by = c("CompetitionID", "SessionID", "GameID", "EndID")
  ) %>%
  mutate(
    Has_Hammer = ifelse(TeamID == Hammer_TeamID, 1, 0)
  )

# View result
View(stones_with_hammer)