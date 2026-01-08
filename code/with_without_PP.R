#
#
# shows the impact of power play by comparing to what would have happened without power play
library(tidyverse)

ends <- read_csv("dfs/ends_processed.csv")
games <- read_csv("dfs/games_processed.csv")
stones <- read_csv("dfs/stones_processed.csv")

# Does PP increase average score for hammer team?
pp_hammer_summary <- ends %>%
  filter(Has_Hammer == 1) %>%
  group_by(Used_PP) %>%
  summarise(
    Avg_Points = mean(Result, na.rm = TRUE),
    Big_End_Rate = mean(Result >= 3),
    Ends = n()
  )

pp_hammer_summary #important bc PP decisions only matter when you have hammer

hammer_ends <- ends %>%
  filter(Has_Hammer == 1)
pp_points     <- hammer_ends %>% filter(Used_PP == 1) %>% pull(Result)
no_pp_points  <- hammer_ends %>% filter(Used_PP == 0) %>% pull(Result)
t_test_result <- t.test(pp_points, no_pp_points, conf.level = 0.95)

t_test_result

ci_summary <- tibble(
  Mean_PP     = mean(pp_points),
  Mean_No_PP  = mean(no_pp_points),
  PP_Effect   = mean(pp_points) - mean(no_pp_points),
  CI_Lower    = t_test_result$conf.int[1],
  CI_Upper    = t_test_result$conf.int[2]
)

ci_summary

# Compute expected non-PP scoring
# estimate baseline scoring when: no Power Play & hammer = yes
baseline_no_pp <- ends %>%
  filter(Used_PP == 0, Has_Hammer == 1) %>%
  summarise(
    Expected_No_PP = mean(Result, na.rm = TRUE)
  ) %>%
  pull(Expected_No_PP)

baseline_no_pp # counterfactual baseline
# If we remove all power-play ends and look only at “normal” ends, 
# gives the average points scored per end

# Replace PP ends with baseline
# Create a “no PP world” version of the data
ends_counterfactual <- ends %>%
  mutate(
    Result_No_PP = case_when(
      Used_PP == 1 & Has_Hammer == 1 ~ baseline_no_pp,
      TRUE ~ Result
    )
  )

# Compare real vs no-PP world
comparison <- ends_counterfactual %>%
  summarise(
    Avg_Actual = mean(Result, na.rm = TRUE),
    Avg_No_PP  = mean(Result_No_PP, na.rm = TRUE),
    PP_Effect  = Avg_Actual - Avg_No_PP
  )

comparison #Per-end average difference

end_dist_comparison <- ends_counterfactual %>%
  mutate(PP_Delta = Result - Result_No_PP) %>%
  summarise(
    Mean_Effect = mean(PP_Delta),
    Median_Effect = median(PP_Delta),
    Positive_Rate = mean(PP_Delta > 0),
    Negative_Rate = mean(PP_Delta < 0),
    Zero_Rate = mean(PP_Delta == 0)
  )

end_dist_comparison #distribution of per-end differences

big_end_comparison <- ends_counterfactual %>%
  summarise(
    Big_End_Actual = mean(Result >= 3),
    Big_End_No_PP  = mean(Result_No_PP >= 3),
    Big_End_Gain   = Big_End_Actual - Big_End_No_PP
  )

big_end_comparison #big-end probability shift

# Save the feature-enhanced dataset
# use this to: plot PP vs non-PP, compare strategies, motivate Monte Carlo or modeling later
write_csv(ends_counterfactual, "dfs/ends_with_counterfactual.csv")
summary(game_level_effect$PP_Gain)


#
#
#PLOTS
library(ggplot2)

# Per-game impact of Power Play
game_level_effect <- ends_counterfactual %>%
  filter(Used_PP == 1 & Has_Hammer == 1) %>%  # ONLY PP ends for hammer team
  group_by(GameUID) %>%
  summarise(
    PP_Gain = sum(Result - Result_No_PP, na.rm = TRUE),
    .groups = "drop"
  )

#
#
# Histogram of PP_Gain (core plot); risk–reward profile 
ggplot(game_level_effect, aes(x = PP_Gain)) +
  geom_histogram(binwidth = 0.5, fill = "steelblue", color = "white") +
  
  # Zero-impact reference line
  geom_vline(xintercept = 0,
             linetype = "dashed",
             color = "red",
             linewidth = 1) +
  
  # Mean PP gain line
  geom_vline(xintercept = mean(game_level_effect$PP_Gain, na.rm = TRUE),
             linetype = "solid",
             color = "darkblue",
             linewidth = 1) +
  
  # Bound to realistic PP impact range
  coord_cartesian(xlim = c(-6, 6)) +
  
  labs(
    title = "Distribution of Power Play Impact per Game",
    subtitle = "Dashed red = no effect, solid blue = average effect",
    x = "Points gained from Power Play (Actual − No PP)",
    y = "Number of games"
  ) +
  
  theme_minimal(base_size = 13)

#
#
# boxplot
ggplot(game_level_effect, aes(x = "", y = PP_Gain)) +
  geom_boxplot(fill = "lightgray", outlier.shape = NA) +
  geom_jitter(
    width = 0.1,
    alpha = 0.3,
    size = 1.5,
    color = "steelblue"
  ) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "red") +
  labs(
    title = "Power Play Impact per Game",
    subtitle = "Each point represents one game",
    x = NULL,
    y = "PP Gain (points)"
  ) +
  theme_minimal()

#
#
# when power plays are most effective
# PP effectiveness by end number
pp_by_end <- ends_counterfactual %>%
  filter(
    Has_Hammer == 1,
    EndID >= 3        # DROP ends 1 & 2
  ) %>%
  group_by(EndID, Used_PP) %>%
  summarise(
    Avg_Points = mean(Result, na.rm = TRUE),
    SE = sd(Result, na.rm = TRUE) / sqrt(n()),
    N = n(),
    .groups = "drop"
  ) %>%
  filter(N >= 20)     # avoid low-sample artifacts

# Visualize
ggplot(pp_by_end,
       aes(x = EndID,
           y = Avg_Points,
           color = factor(Used_PP),
           group = Used_PP)) +
  geom_line(linewidth = 1) +
  geom_point(size = 2) +
  geom_errorbar(
    aes(
      ymin = Avg_Points - 1.96 * SE,
      ymax = Avg_Points + 1.96 * SE
    ),
    width = 0.15,
    alpha = 0.6
  ) +
  scale_color_manual(
    values = c("0" = "#F8766D", "1" = "#00BFC4"),
    labels = c("No Power Play", "Power Play")
  ) +
  scale_x_continuous(breaks = 3:8, limits = c(3, 8)) +
  labs(
    title = "Power Play Effectiveness by End (Hammer Team)",
    subtitle = "Ends 3–8 only; points show mean ± 95% CI",
    x = "End",
    y = "Average Points Scored",
    color = ""
  ) +
  theme_minimal(base_size = 13)


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

pp_lr_context <- ends_with_context %>%
  filter(Used_PP == 1, Has_Hammer == 1) %>%
  mutate(
    PP_Side = case_when(
      PowerPlay == 1 ~ "Right",
      PowerPlay == 2 ~ "Left"
    ),
    Score_Context = case_when(
      Score_Diff_Before < 0 ~ "Behind",
      Score_Diff_Before == 0 ~ "Tied",
      TRUE ~ "Ahead"
    )
  ) %>%
  group_by(EndID, Score_Context, PP_Side) %>%
  summarise(
    Avg_Score = mean(Result),
    Big_End_Rate = mean(Result >= 3),
    N = n(),
    .groups = "drop"
  ) %>%
  filter(N >= 10)

lm_pp <- lm(
  Result ~ PP_Side + EndID + Score_Diff_Before,
  data = ends_with_context %>%
    filter(Used_PP == 1, Has_Hammer == 1, PowerPlay %in% c(1, 2)) %>%
    mutate(
      PP_Side = if_else(PowerPlay == 1, "Right", "Left")  # 1=Right, 2=Left
    )
)

summary(lm_pp)