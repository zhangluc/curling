# STILL WORKING ON THE GRAPHS (SOME AREN'T ENTIRELY CORRECT & TRYNA ADD MORE)
#
#
# shows the impact of power play by comparing to what would have happened wihtout power play
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
write_csv(ends_counterfactual, "dfs/ends_with_counterfactual.csv")
summary(game_level_effect$PP_Gain)

#results:
#imply that Power Play should be used: When geometry is favorable, Against certain opponents, In specific game states
#motivates Feature engineering, Conditional models, Simulation-based decision rules


#
#
#PLOTS
library(ggplot2)

#
# fix
# Histogram of PP_Gain (core plot); risk–reward profile 
ggplot(game_level_effect, aes(x = PP_Gain)) +
  geom_histogram(binwidth = 0.5, fill = "steelblue", color = "white") +
  geom_vline(xintercept = 0, linetype = "dashed", color = "red") +
  labs(
    title = "Distribution of Power Play Impact per Game",
    x = "Points gained from Power Play (Actual − No PP)",
    y = "Number of games"
  )

#
#
# boxplot
# look into: why are there only three dots????
ggplot(game_level_effect, aes(y = PP_Gain)) +
  geom_boxplot(fill = "lightgray") +
  geom_hline(yintercept = 0, linetype = "dashed", color = "red") +
  labs(
    title = "Power Play Impact per Game",
    y = "PP Gain (points)"
  )

#
# fix
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

#
#
# when power plays are most effective
# PP effectiveness by end number
pp_by_end <- ends_counterfactual %>%
  filter(Has_Hammer == 1) %>%
  group_by(EndID, Used_PP) %>%
  summarise(
    Avg_Points = mean(Result, na.rm = TRUE),
    N = n()
  )

# Visualize
ggplot(pp_by_end, aes(x = EndID, y = Avg_Points, color = factor(Used_PP))) +
  geom_line() +
  geom_point() +
  scale_x_continuous(
    breaks = 1:8,
    limits = c(1, 8)
  ) +
  labs(title = "Power Play Effectiveness by End",
       color = "Used PP")

#
#
# score differential analysis
# Add score differential context to your ends data
# You'll need to calculate running score for each game
# Create opponent result by joining the data with itself
ends_with_context <- ends_counterfactual %>%
  arrange(GameUID, EndID) %>%
  group_by(GameUID, EndID) %>%
  mutate(
    # For each row, get the OTHER team's result in the same end
    Opponent_Result = if_else(
      row_number() == 1,
      Result[2],
      Result[1]
    )
  ) %>%
  ungroup() %>%
  group_by(GameUID, TeamID) %>%
  arrange(GameUID, TeamID, EndID) %>%
  mutate(
    # Calculate cumulative scores for this team and opponent
    Cumulative_Score = cumsum(Result),
    Opponent_Cumulative = cumsum(Opponent_Result),
    # Score differential BEFORE this end
    Score_Diff_Before = lag(Cumulative_Score, default = 0) - 
      lag(Opponent_Cumulative, default = 0)
  ) %>%
  ungroup()

# Now analyze PP usage by game situation
pp_timing <- ends_with_context %>%
  filter(Has_Hammer == 1, Used_PP == 1) %>%
  summarise(
    Avg_End = mean(EndID),
    Avg_Score_Diff = mean(Score_Diff_Before, na.rm = TRUE),
    Median_Score_Diff = median(Score_Diff_Before, na.rm = TRUE),
    N = n()
  )

print(pp_timing)

# Visualize when PP is used
ggplot(ends_with_context %>% filter(Has_Hammer == 1, Used_PP == 1), 
       aes(x = EndID, y = Score_Diff_Before)) +
  geom_jitter(width = 0.2, alpha = 0.5, color = "blue") +
  geom_hline(yintercept = 0, linetype = "dashed", color = "red") +
  stat_summary(fun = mean, geom = "line", color = "darkblue", size = 1) +
  labs(
    title = "When Teams Use Power Play",
    x = "End Number",
    y = "Score Differential Before End",
    subtitle = "Each point = one PP usage"
  )


#
#
# PP Success by Game Context
pp_success_context <- ends_with_context %>%
  filter(Used_PP == 1, Has_Hammer == 1) %>%
  mutate(
    Game_Context = case_when(
      Score_Diff_Before < -3 ~ "Behind >3",
      Score_Diff_Before < 0 ~ "Behind 1-3",
      Score_Diff_Before == 0 ~ "Tied",
      Score_Diff_Before <= 3 ~ "Ahead 1-3",
      TRUE ~ "Ahead >3"
    ),
    Game_Context = factor(Game_Context, 
                          levels = c("Behind >3", "Behind 1-3", "Tied", 
                                     "Ahead 1-3", "Ahead >3")),
    PP_Gain = Result - Result_No_PP
  )

# Summary stats for the plot
pp_context_summary <- pp_success_context %>%
  group_by(EndID, Game_Context) %>%
  summarise(
    Avg_PP_Gain = mean(PP_Gain),
    N = n(),
    SE = sd(PP_Gain) / sqrt(N),
    .groups = "drop"
  ) %>%
  filter(N >= 5)  # Only show contexts with at least 5 observations

#heatmap of PP Success
ggplot(pp_context_summary, aes(x = EndID, y = Game_Context, fill = Avg_PP_Gain)) +
  geom_tile(color = "white", size = 0.5) +
  geom_text(aes(label = sprintf("%.2f\n(n=%d)", Avg_PP_Gain, N)), 
            size = 3, color = "black") +
  scale_fill_gradient2(low = "red", mid = "white", high = "darkgreen", 
                       midpoint = 0, limits = c(-2, 2),
                       name = "PP Gain\n(vs baseline)") +
  labs(
    title = "Power Play Effectiveness by Game Context",
    subtitle = "Average points gained above baseline (1.14 pts)",
    x = "End Number",
    y = "Score Situation"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(face = "bold", size = 14),
    axis.text = element_text(size = 10)
  )

#
#
# left vs right pp (table)
# Test if left/right PP matters
left_right_analysis <- ends_with_context %>%
  filter(Used_PP == 1, Has_Hammer == 1) %>%
  mutate(
    PP_Side = case_when(
      PowerPlay == 1 ~ "Right",
      PowerPlay == 2 ~ "Left",
      TRUE ~ "Unknown"
    )
  ) %>%
  group_by(PP_Side, EndID) %>%
  summarise(
    Avg_Score = mean(Result),
    Big_End_Rate = mean(Result >= 3),
    N = n(),
    .groups = "drop"
  )

# Statistical test
left_results <- ends_with_context %>% 
  filter(PowerPlay == 2, Has_Hammer == 1) %>% 
  pull(Result)

right_results <- ends_with_context %>% 
  filter(PowerPlay == 1, Has_Hammer == 1) %>% 
  pull(Result)

t_test <- t.test(left_results, right_results)

print("Left vs Right PP Comparison:")
print(left_right_analysis)
print(paste("T-test p-value:", round(t_test$p.value, 4)))

