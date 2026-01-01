# STILL WORKING ON ISSUES !!!
#
#
#opening shot analysis

# Disable RStudio's automatic data caching to avoid errors
options(rstudio.data.viewer = FALSE)

library(tidyverse)

# Read the data files - use suppressMessages to avoid cache warnings
stones_processed <- suppressMessages(read_csv("dfs/stones_processed.csv"))
ends_counterfactual <- suppressMessages(read_csv("dfs/ends_with_counterfactual.csv"))

# Task labels for shot types
task_labels <- c(
  "0" = "Draw",
  "1" = "Front",
  "2" = "Guard",
  "3" = "Raise/Tap-back",
  "4" = "Wick/Soft Peel",
  "5" = "Freeze",
  "6" = "Take-out",
  "7" = "Hit and Roll",
  "8" = "Clearing",
  "9" = "Double Take-out",
  "10" = "Promotion Take-out",
  "11" = "Through",
  "13" = "No statistics"
)

# ============================================================================
# DIAGNOSTIC: Check the data
# ============================================================================

cat("=== DIAGNOSTIC INFO ===\n")
cat("Total stones rows:", nrow(stones_processed), "\n")
cat("Total ends rows:", nrow(ends_counterfactual), "\n")
cat("Stones with first 3 shots (7,8,9):", nrow(stones_processed %>% filter(ShotID %in% c(7, 8, 9))), "\n")
cat("Ends with PP=1 and Hammer=1:", nrow(ends_counterfactual %>% filter(Used_PP == 1, Has_Hammer == 1)), "\n")
cat("Ends with PP=0 and Hammer=1:", nrow(ends_counterfactual %>% filter(Used_PP == 0, Has_Hammer == 1)), "\n\n")

# ============================================================================
# SHOT TYPE EFFECTIVENESS
# ============================================================================

cat("Analyzing shot types (first 3 shots = ShotID 7, 8, 9)...\n")

# Do the join and filtering step by step to avoid cache issues
stones_first_3 <- stones_processed %>% filter(ShotID %in% c(7, 8, 9))

shot_joined <- inner_join(
  stones_first_3, 
  ends_counterfactual, 
  by = c("GameUID", "EndID", "TeamID")
)

shot_type_effectiveness <- stones_processed %>%
  filter(ShotID %in% c(7, 8, 9)) %>%
  inner_join(ends_counterfactual, 
             by = c("GameUID", "EndID", "TeamID"),
             relationship = "many-to-one") %>%  # Each stone matches one end result
  rename(Has_Hammer_Stone = Has_Hammer.x, Has_Hammer_End = Has_Hammer.y) %>%
  filter(Has_Hammer_Stone == 1) %>%
  group_by(Task, Used_PP) %>%
  summarise(
    Avg_Shot_Quality = mean(Points, na.rm = TRUE),
    Avg_End_Result = mean(Result),
    N = n(),
    .groups = "drop"
  )

#
#
# Find ALL duplicates (not just view them)
duplicates_full <- ends_counterfactual %>%
  group_by(GameUID, EndID, TeamID) %>%
  filter(n() > 1) %>%
  arrange(GameUID, EndID, TeamID) %>%
  ungroup()

# Show the full GameUID without truncation
duplicates_full %>%
  select(GameUID, EndID, TeamID, Has_Hammer, Result, ClusterIndex) %>%
  print(n = Inf, width = Inf)

# Check for consecutive shots by same team
stones_processed %>%
  arrange(GameUID, EndID, ShotID) %>%
  group_by(GameUID, EndID) %>%
  mutate(
    Next_Team = lead(TeamID),
    Same_Team_Consecutive = (TeamID == Next_Team)
  ) %>%
  filter(Same_Team_Consecutive == TRUE) %>%
  select(GameUID, EndID, ShotID, TeamID, Next_Team) %>%
  head(20)

cat("Shot types before filtering (N>=20):\n")
print(as.data.frame(shot_type_effectiveness))  # Convert to data.frame to avoid cache

# Now filter for N >= 20
shot_type_effectiveness <- shot_type_effectiveness %>%
  filter(N >= 20)

cat("\nShot types after filtering (N>=20):\n")
print(as.data.frame(shot_type_effectiveness))

# Use FULL JOIN instead of INNER JOIN to keep all shot types
shot_no_pp <- shot_type_effectiveness %>%
  filter(Used_PP == 0) %>%
  select(Task, 
         Avg_Shot_Quality_No_PP = Avg_Shot_Quality,
         Avg_End_Result_No_PP = Avg_End_Result,
         N_No_PP = N)

shot_with_pp <- shot_type_effectiveness %>%
  filter(Used_PP == 1) %>%
  select(Task,
         Avg_Shot_Quality_PP = Avg_Shot_Quality,
         Avg_End_Result_PP = Avg_End_Result,
         N_PP = N)

shot_recommendations <- full_join(shot_no_pp, shot_with_pp, by = "Task") %>%
  mutate(
    PP_Advantage = Avg_End_Result_PP - Avg_End_Result_No_PP,
    Shot_Type = recode(as.character(Task), !!!task_labels, .default = "Unknown")
  ) %>%
  select(Shot_Type, Task, PP_Advantage, everything()) %>%
  arrange(desc(PP_Advantage))

cat("\n=== BEST SHOT TYPES FOR POWER PLAY ===\n")
print(as.data.frame(shot_recommendations))

# ============================================================================
# ALTERNATIVE: Lower threshold to N >= 10
# ============================================================================

cat("\n\n=== ALTERNATIVE: LOWER THRESHOLD (N >= 10) ===\n")

shot_type_effectiveness_lower <- shot_joined %>%
  rename(Has_Hammer_Stone = Has_Hammer.x, Has_Hammer_End = Has_Hammer.y) %>%
  filter(Has_Hammer_Stone == 1) %>%
  group_by(Task, Used_PP) %>%
  summarise(
    Avg_Shot_Quality = mean(Points, na.rm = TRUE),
    Avg_End_Result = mean(Result),
    N = n(),
    .groups = "drop"
  ) %>%
  filter(N >= 10)

shot_no_pp_lower <- shot_type_effectiveness_lower %>%
  filter(Used_PP == 0) %>%
  select(Task, 
         Avg_Shot_Quality_No_PP = Avg_Shot_Quality,
         Avg_End_Result_No_PP = Avg_End_Result,
         N_No_PP = N)

shot_with_pp_lower <- shot_type_effectiveness_lower %>%
  filter(Used_PP == 1) %>%
  select(Task,
         Avg_Shot_Quality_PP = Avg_Shot_Quality,
         Avg_End_Result_PP = Avg_End_Result,
         N_PP = N)

shot_recommendations_lower <- full_join(shot_no_pp_lower, shot_with_pp_lower, by = "Task") %>%
  filter(!is.na(Avg_End_Result_PP) & !is.na(Avg_End_Result_No_PP)) %>%
  mutate(
    PP_Advantage = Avg_End_Result_PP - Avg_End_Result_No_PP,
    Shot_Type = recode(as.character(Task), !!!task_labels, .default = "Unknown")
  ) %>%
  select(Shot_Type, Task, PP_Advantage, everything()) %>%
  arrange(desc(PP_Advantage))

print(as.data.frame(shot_recommendations_lower), width = Inf)

# ============================================================================
# OPENING SEQUENCES
# ============================================================================

cat("\n\nAnalyzing opening sequences (first 3 shots = ShotID 7, 8, 9)...\n")

opening_sequences <- stones_first_3 %>%
  group_by(GameUID, EndID, TeamID) %>%
  arrange(ShotID) %>%
  summarise(
    Sequence = paste(Task[1:min(3, n())], collapse = " -> "),
    Avg_Quality = mean(Points, na.rm = TRUE),
    N_Shots = n(),
    .groups = "drop"
  ) %>%
  inner_join(ends_counterfactual, by = c("GameUID", "EndID", "TeamID")) %>%
  filter(Has_Hammer == 1, N_Shots == 3)

cat("Total sequences found:", nrow(opening_sequences), "\n")
cat("PP sequences:", sum(opening_sequences$Used_PP == 1), "\n")

top_pp_sequences <- opening_sequences %>%
  filter(Used_PP == 1) %>%
  group_by(Sequence) %>%
  summarise(
    Avg_Result = mean(Result),
    Avg_Quality = mean(Avg_Quality),
    Big_End_Rate = mean(Result >= 3),
    N = n(),
    .groups = "drop"
  ) %>%
  filter(N >= 5) %>%
  arrange(desc(Avg_Result))

cat("Unique PP sequences (N>=5):", nrow(top_pp_sequences), "\n")

# Decode sequences
top_pp_sequences_decoded <- top_pp_sequences %>%
  mutate(Sequence_Decoded = Sequence)

for (task_num in names(task_labels)) {
  top_pp_sequences_decoded <- top_pp_sequences_decoded %>%
    mutate(
      Sequence_Decoded = str_replace_all(
        Sequence_Decoded, 
        paste0("\\b", task_num, "\\b"), 
        task_labels[task_num]
      )
    )
}

cat("\n=== TOP OPENING SEQUENCES WITH POWER PLAY ===\n")
result_seq <- head(select(top_pp_sequences_decoded, Sequence_Decoded, Avg_Result, Big_End_Rate, N), 15)
print(as.data.frame(result_seq))

# ============================================================================
# FIRST SHOT ANALYSIS
# ============================================================================

cat("\n\nAnalyzing first shots (ShotID = 7)...\n")

first_shot_data <- stones_processed %>% filter(ShotID == 7)

first_shot_joined <- inner_join(
  first_shot_data,
  ends_counterfactual,
  by = c("GameUID", "EndID", "TeamID")
)

first_shot_analysis <- first_shot_joined %>%
  rename(Has_Hammer_Stone = Has_Hammer.x, Has_Hammer_End = Has_Hammer.y) %>%
  filter(Has_Hammer_Stone == 1) %>%
  group_by(Task, Used_PP) %>%
  summarise(
    Avg_Shot_Quality = mean(Points, na.rm = TRUE),
    Avg_End_Result = mean(Result),
    Big_End_Rate = mean(Result >= 3),
    N = n(),
    .groups = "drop"
  ) %>%
  filter(N >= 5)

cat("First shot analysis rows:", nrow(first_shot_analysis), "\n")

first_no_pp <- first_shot_analysis %>%
  filter(Used_PP == 0) %>%
  select(Task,
         Avg_End_Result_No_PP = Avg_End_Result,
         Big_End_Rate_No_PP = Big_End_Rate,
         N_No_PP = N)

first_with_pp <- first_shot_analysis %>%
  filter(Used_PP == 1) %>%
  select(Task,
         Avg_End_Result_PP = Avg_End_Result,
         Big_End_Rate_PP = Big_End_Rate,
         N_PP = N)

first_shot_comparison <- full_join(first_no_pp, first_with_pp, by = "Task") %>%
  filter(!is.na(Avg_End_Result_PP) & !is.na(Avg_End_Result_No_PP)) %>%
  mutate(
    PP_Advantage = Avg_End_Result_PP - Avg_End_Result_No_PP,
    Shot_Type = recode(as.character(Task), !!!task_labels, .default = "Unknown")
  ) %>%
  select(Shot_Type, Task, PP_Advantage, everything()) %>%
  arrange(desc(PP_Advantage))

cat("\n=== BEST FIRST SHOT TYPES FOR POWER PLAY ===\n")
print(as.data.frame(first_shot_comparison))

# ============================================================================
# KEY INSIGHTS SUMMARY
# ============================================================================

cat("\n\n╔════════════════════════════════════════════════════════════╗\n")
cat("║                    KEY INSIGHTS                            ║\n")
cat("╚════════════════════════════════════════════════════════════╝\n")

if (nrow(shot_recommendations_lower) > 0) {
  cat("\n1. BEST SHOT TYPES WITH PP (by advantage):\n")
  top_3_shots <- head(shot_recommendations_lower, 3)
  for (i in 1:nrow(top_3_shots)) {
    cat(sprintf("   %d. %s: +%.2f points (%.2f PP vs %.2f no PP, n=%d/%d)\n",
                i,
                top_3_shots$Shot_Type[i],
                top_3_shots$PP_Advantage[i],
                top_3_shots$Avg_End_Result_PP[i],
                top_3_shots$Avg_End_Result_No_PP[i],
                top_3_shots$N_PP[i],
                top_3_shots$N_No_PP[i]))
  }
}

if (nrow(top_pp_sequences_decoded) > 0) {
  cat("\n2. MOST SUCCESSFUL PP SEQUENCES:\n")
  top_3_seq <- head(top_pp_sequences_decoded, 3)
  for (i in 1:nrow(top_3_seq)) {
    cat(sprintf("   %d. %s\n      Avg: %.2f pts | Big End: %.1f%% | n=%d\n",
                i,
                top_3_seq$Sequence_Decoded[i],
                top_3_seq$Avg_Result[i],
                top_3_seq$Big_End_Rate[i] * 100,
                top_3_seq$N[i]))
  }
}

if (nrow(first_shot_comparison) > 0) {
  cat("\n3. BEST FIRST SHOT WITH PP:\n")
  best_first <- head(first_shot_comparison, 1)
  cat(sprintf("   %s: +%.2f advantage (%.2f PP vs %.2f no PP)\n",
              best_first$Shot_Type[1],
              best_first$PP_Advantage[1],
              best_first$Avg_End_Result_PP[1],
              best_first$Avg_End_Result_No_PP[1]))
}

cat("\n")
cat("Analysis complete!\n")