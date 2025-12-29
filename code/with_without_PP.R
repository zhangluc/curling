library(tidyverse)

ends <- read_csv("dfs/ends_processed.csv")
games <- read_csv("dfs/games_processed.csv")
stones <- read_csv("dfs/stones_processed.csv")

# Create a simple PP indicator
ends <- ends %>%
  mutate(
    Used_PP = ifelse(is.na(PowerPlay) | PowerPlay == 0, 0, 1)
  )

# Compare scoring with vs without Power Play
pp_summary <- ends %>%
  group_by(Used_PP) %>%
  summarise(
    Avg_Points = mean(Result, na.rm = TRUE),
    Median_Points = median(Result, na.rm = TRUE),
    Big_End_Rate = mean(Result >= 3, na.rm = TRUE),
    Ends = n()
  )

pp_summary #answers: Does PP increase average score? & Does it increase big ends (3+)?

# Same comparison only when team has hammer
pp_hammer_summary <- ends %>%
  filter(Has_Hammer == 1) %>%
  group_by(Used_PP) %>%
  summarise(
    Avg_Points = mean(Result, na.rm = TRUE),
    Big_End_Rate = mean(Result >= 3),
    Ends = n()
  )

pp_hammer_summary #important bc PP decisions only matter when you have hammer

# Compute expected non-PP scoring
# estimate baseline scoring when: no Power Play & hammer = yes
baseline_no_pp <- ends %>%
  filter(Used_PP == 0, Has_Hammer == 1) %>%
  summarise(
    Expected_No_PP = mean(Result, na.rm = TRUE)
  ) %>%
  pull(Expected_No_PP)

baseline_no_pp # counterfactual baseline
# If we remove all power-play ends and look only at “normal” ends, gives the average points scored per end

# Replace PP ends with baseline
# Create a “no PP world” version of the data
ends_counterfactual <- ends %>%
  mutate(
    Result_No_PP = case_when(
      Used_PP == 1 & Has_Hammer == 1 ~ baseline_no_pp,
      TRUE ~ Result
    )
  )

# Compare total scoring: real vs no-PP world
comparison <- ends_counterfactual %>%
  summarise(
    Actual_Total = sum(Result, na.rm = TRUE),
    No_PP_Total = sum(Result_No_PP, na.rm = TRUE),
    Difference = Actual_Total - No_PP_Total
  )

comparison

# Per-game impact of Power Play
game_level_effect <- ends_counterfactual %>%
  group_by(GameUID) %>%
  summarise(
    Actual = sum(Result, na.rm = TRUE),
    No_PP = sum(Result_No_PP, na.rm = TRUE),
    PP_Gain = Actual - No_PP,
    .groups = "drop"
  )

# Save the feature-enhanced dataset
# use this to: plot PP vs non-PP, compare strategies, motivate Monte Carlo or modeling later
write_csv(ends_counterfactual, "ends_with_counterfactual.csv")
summary(game_level_effect$PP_Gain)

#results:
#imply that Power Play should be used: When geometry is favorable, Against certain opponents, In specific game states
#motivates Feature engineering, Conditional models, Simulation-based decision rules

#
#
#PLOTS
library(ggplot2)

# Histogram of PP_Gain (core plot); risk–reward profile 
ggplot(game_level_effect, aes(x = PP_Gain)) +
  geom_histogram(binwidth = 0.5, fill = "steelblue", color = "white") +
  geom_vline(xintercept = 0, linetype = "dashed", color = "red") +
  labs(
    title = "Distribution of Power Play Impact per Game",
    x = "Points gained from Power Play (Actual − No PP)",
    y = "Number of games"
  )

# boxplot
ggplot(game_level_effect, aes(y = PP_Gain)) +
  geom_boxplot(fill = "lightgray") +
  geom_hline(yintercept = 0, linetype = "dashed", color = "red") +
  labs(
    title = "Power Play Impact per Game",
    y = "PP Gain (points)"
  )

# Team-level average PP_Gain
team_effect <- ends_counterfactual %>%
  group_by(TeamID) %>%
  summarise(mean_PP_Gain = mean(Result - Result_No_PP))

ggplot(team_effect, aes(x = reorder(TeamID, mean_PP_Gain), y = mean_PP_Gain)) +
  geom_col(fill = "darkgreen") +
  coord_flip() +
  labs(
    title = "Average Power Play Impact by Team",
    x = "Team",
    y = "Average PP Gain"
  )