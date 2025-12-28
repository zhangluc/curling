# adds Hammer_TeamID & Has_Hammer column to Stones.csv (0 = no hammer, 1 = has hammer)

library(readr)
library(dplyr)

# Load Stones.csv
stones <- read_csv("dfs/Stones.csv")

# Step 1: Identify hammer team per end
hammer_by_end <- stones %>%
  group_by(CompetitionID, SessionID, GameID, EndID) %>%
  slice_max(order_by = ShotID, n = 1, with_ties = FALSE) %>%
  ungroup() %>%
  select(CompetitionID, SessionID, GameID, EndID,
         Hammer_TeamID = TeamID)

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

# Optional: save
write_csv(stones_with_hammer, "dfs/stones_with_hammer.csv")

#makes sure that the number of teams that have the hammer per end is 1
stones_with_hammer %>%
  group_by(CompetitionID, SessionID, GameID, EndID) %>%
  summarise(
    n_hammer_teams = n_distinct(TeamID[Has_Hammer == 1])
  )

hammer_check <- hammer_by_end %>%
  arrange(CompetitionID, SessionID, GameID, EndID) %>%
  group_by(CompetitionID, SessionID, GameID) %>%
  mutate(
    PrevHammer = lag(Hammer_TeamID),
    Switched = ifelse(is.na(PrevHammer), NA, Hammer_TeamID != PrevHammer)
  ) %>%
  ungroup()

# overall switch rate (ignores first end of each game)
mean(hammer_check$Switched, na.rm = TRUE) #if n>1, it does NOT alternate every end in your data (shows how often it doesn’t).

# how many switched vs not
table(hammer_check$Switched, useNA = "ifany")
#interpretation of table:
#•	TRUE → hammer changed from last end
#•	FALSE → hammer stayed the same
#•	NA → first end of a game (no previous end to compare)'''