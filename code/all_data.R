#currently: loads all CSVs into one data frame
# IMPORTANT: assumes that data is in a separate folder next to github repo
# make sure wd is right
# starting wd: /Users/luciazhang/Desktop/R/curling/curling-code (open the R project)

# load required packages
library(readr)
library(dplyr)

# clear environment
rm(list = ls())

# define data directory
data_dir <- "../2026-main"

# sanity check — should list the CSV files
print(list.files(data_dir))

# load all CSVs into data frames
#view the files: View(competition)
competition <- read_csv(file.path(data_dir, "Competition.csv"))
competitors <- read_csv(file.path(data_dir, "Competitors.csv"))
ends <- read_csv(file.path(data_dir, "Ends.csv"))
games <- read_csv(file.path(data_dir, "Games.csv"))
stones <- read_csv(file.path(data_dir, "Stones.csv"))
teams <- read_csv(file.path(data_dir, "Teams.csv"))

# sanity checks
# can comment out
message("Data loaded successfully:")
message(paste("Competition rows: ", nrow(competition)))
message(paste("Competitors rows: ", nrow(competitors)))
message(paste("Ends rows: ", nrow(ends)))
message(paste("Games rows: ", nrow(games)))
message(paste("Stones rows: ", nrow(stones)))
message(paste("Teams rows: ", nrow(teams)))
