# ============================================================
# Opening Shot Analysis — Mixed Doubles Curling
# Focus:
#   • ShotID = 7  (non-hammer opening shot)
#   • ShotID = 8  (hammer response)
# Includes:
#   A. Non-hammer opening shot effectiveness
#   B. Hammer response conditional on opening shot
#   C. Heatmap visualization
#   D. Publication-ready table
# ============================================================

library(tidyverse)
library(gt)

# ------------------------------------------------------------
# 0. Load data
# ------------------------------------------------------------
stones <- read_csv("dfs/stones_processed.csv")
ends   <- read_csv("dfs/ends_with_counterfactual.csv")

# Shot type labels
task_labels <- c(
  "0"  = "Draw",
  "1"  = "Front",
  "2"  = "Guard",
  "3"  = "Raise/Tap-back",
  "4"  = "Wick/Soft Peel",
  "5"  = "Freeze",
  "6"  = "Take-out",
  "7"  = "Hit and Roll",
  "8"  = "Clearing",
  "9"  = "Double Take-out",
  "10" = "Promotion Take-out",
  "11" = "Through"
)

# ============================================================
# A. NON-HAMMER OPENING SHOT EFFECTIVENESS (ShotID = 7)
# ============================================================

opening_shot_nonhammer <- stones %>%
  filter(ShotID == 7) %>%
  inner_join(
    ends,
    by = c("GameUID", "EndID", "TeamID")
  ) %>%
  rename(
    Has_Hammer_Stone = Has_Hammer.x,
    Has_Hammer_End   = Has_Hammer.y
  ) %>%
  filter(Has_Hammer_Stone == 0)   # team that throws first

opening_shot_summary <- opening_shot_nonhammer %>%
  group_by(Task, Used_PP) %>%
  summarise(
    Avg_Execution  = mean(Points, na.rm = TRUE),          # shot execution (0–4)
    Avg_End_Points = mean(Result.y, na.rm = TRUE),        # points scored in end
    Big_End_Rate   = mean(Result.y >= 3, na.rm = TRUE),   # P(end ≥ 3)
    N = n(),
    .groups = "drop"
  ) %>%
  filter(N >= 20) %>%                                     # stability threshold
  mutate(
    Shot_Type   = recode(as.character(Task), !!!task_labels),
    Opponent_PP = ifelse(Used_PP == 1, "Opponent Used PP", "No Power Play")
  ) %>%
  arrange(Opponent_PP, desc(Avg_End_Points))

print(opening_shot_summary)

# ============================================================
# B. HAMMER RESPONSE CONDITIONAL ON OPENING SHOT
# ShotID = 8 given ShotID = 7
# ============================================================

# First (non-hammer) shot
first_shot <- stones %>%
  filter(ShotID == 7) %>%
  select(GameUID, EndID, First_Task = Task)

# Hammer response
hammer_response <- stones %>%
  filter(ShotID == 8) %>%
  inner_join(
    ends,
    by = c("GameUID", "EndID", "TeamID")
  ) %>%
  rename(
    Has_Hammer_Stone = Has_Hammer.x,
    Has_Hammer_End   = Has_Hammer.y
  ) %>%
  filter(Has_Hammer_Stone == 1)

response_analysis <- hammer_response %>%
  inner_join(first_shot, by = c("GameUID", "EndID")) %>%
  group_by(First_Task, Task, Used_PP) %>%
  summarise(
    Avg_Execution  = mean(Points, na.rm = TRUE),
    Avg_End_Points = mean(Result.y, na.rm = TRUE),
    Big_End_Rate   = mean(Result.y >= 3),
    N = n(),
    .groups = "drop"
  ) %>%
  filter(N >= 15) %>%
  mutate(
    First_Shot  = recode(as.character(First_Task), !!!task_labels),
    Hammer_Shot = recode(as.character(Task), !!!task_labels)
  ) %>%
  arrange(desc(Avg_End_Points))

print(response_analysis)

# ============================================================
# C. VISUALIZATION — HAMMER RESPONSE HEATMAP
# ============================================================

plot_data <- response_analysis %>%
  mutate(
    Used_PP = factor(Used_PP, labels = c("No Power Play", "Power Play")),
    First_Shot  = factor(First_Shot),
    Hammer_Shot = factor(Hammer_Shot)
  )

midpoint_score <- mean(plot_data$Avg_End_Points, na.rm = TRUE)

ggplot(plot_data,
       aes(x = First_Shot, y = Hammer_Shot, fill = Avg_End_Points)) +
  geom_tile(color = "grey85", linewidth = 0.5) +
  geom_text(aes(label = round(Avg_End_Points, 2)),
            size = 3.5, fontface = "bold") +
  facet_wrap(~ Used_PP, nrow = 1) +
  scale_fill_gradient2(
    low = "#b2182b",     # red
    mid = "white",
    high = "#1a9850",   # green
    midpoint = midpoint_score,
    name = "Avg End Points"
  ) +
  labs(
    title = "Hammer Team Response to Opening Shot",
    subtitle = "Average end points scored by hammer team (ShotID = 8)",
    x = "Opponent Opening Shot (ShotID = 7)",
    y = "Hammer Response Shot (ShotID = 8)"
  ) +
  coord_fixed() +
  theme_minimal(base_size = 13) +
  theme(
    panel.grid = element_blank(),
    axis.text.x = element_text(angle = 30, hjust = 1),
    strip.text = element_text(face = "bold")
  )

# ============================================================
# D. PUBLICATION-READY TABLE
# Non-hammer opening shot (no opponent power play)
# ============================================================

opening_shot_summary %>%
  filter(Opponent_PP == "No Power Play") %>%
  select(Shot_Type, Avg_Execution, Avg_End_Points, Big_End_Rate, N) %>%
  gt() %>%
  fmt_number(
    columns = c(Avg_Execution, Avg_End_Points, Big_End_Rate),
    decimals = 2
  ) %>%
  cols_label(
    Shot_Type      = "Opening Shot",
    Avg_Execution  = "Avg Execution (0–4)",
    Avg_End_Points = "Avg End Points",
    Big_End_Rate   = "Big End Rate",
    N              = "Ends"
  ) %>%
  tab_header(
    title = "Effectiveness of Opening Shot for Non-Hammer Team (No Power Play)"
  )