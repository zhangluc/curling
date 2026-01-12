# Curling Power Play & Opening Shot Analysis (Mixed Doubles)

This repository contains a full empirical analysis of **Power Play strategy and opening shot effectiveness in mixed doubles curling**, using official competition data.

The project:

* Builds cleaned datasets from raw CSVs
* Constructs hammer/team context
* Estimates counterfactual outcomes without Power Play
* Measures Power Play impact at the end, game, and season level
* Analyzes opening shot strategy and hammer response
* Produces publication-ready figures and tables

---

## Repository Structure

```
.
├── code
│   ├── all_data.R
│   ├── opening_shot_analysis.R
│   ├── stones_with_hammer.R
│   └── with_without_PP.R
├── data
│   ├── Competition.csv
│   ├── Competitors.csv
│   ├── Ends.csv
│   ├── Games.csv
│   ├── stones_with_hammer.csv
│   ├── Stones.csv
│   └── Teams.csv
├── dfs
│   ├── Competition.csv
│   ├── Competitors.csv
│   ├── ends_with_counterfactual.csv
│   ├── Ends.csv
│   ├── Games.csv
│   ├── stones_with_hammer.csv
│   ├── Stones.csv
│   └── Teams.csv
├── figures
│   ├── avg_pp_impact.png
│   ├── histogram_pp_impact.png
│   ├── pp_effective_by_end.png
│   ├── pp_impact_boxplot.png
│   └── when_teams_use_pp.png
├── README.md
└── useful_commands.md
```

---

## Project Overview

This project studies **Power Play strategy in elite mixed doubles curling** using full shot-level and end-level data.

The core questions:

* Does Power Play increase scoring for the hammer team?
* When is Power Play most effective?
* How large is the game-level impact of Power Play?
* When do teams choose to use Power Play?
* Which opening shots lead to the best outcomes?
* How does hammer respond to different opening strategies?

The analysis uses:

* End-level scoring outcomes
* Shot-level execution data
* Hammer context
* Counterfactual modeling (what would have happened without PP)

---

## Data

### Raw Data (`/data`)

Official competition datasets:

* `Competition.csv`
* `Competitors.csv`
* `Games.csv`
* `Ends.csv`
* `Stones.csv`
* `Teams.csv`

### Processed Data (`/dfs`)

Cleaned and feature-engineered versions:

* `stones_with_hammer.csv` — shot-level data with hammer flag
* `ends_processed.csv` — end-level dataset
* `ends_with_counterfactual.csv` — includes no-PP counterfactual outcomes
* `games_processed.csv` — game-level metadata

---

## Analysis Pipeline

### 1. Load and Stage Data

**Script:** `code/all_data.R`

Purpose:

* Loads all raw CSV files
* Performs sanity checks
* Writes cleaned copies into `/dfs`

This script assumes your data directory is adjacent to the repo.

---

### 2. Add Hammer Context

**Script:** `code/stones_with_hammer.R`

Purpose:

* Identifies hammer team per end
* Adds:

  * `Hammer_TeamID`
  * `Has_Hammer` (1 = hammer, 0 = non-hammer)
* Validates hammer alternation behavior

Output:

```
dfs/stones_with_hammer.csv
```

This enables all hammer-conditional analysis.

---

### 3. Power Play Impact & Counterfactual Modeling

**Script:** `code/with_without_PP.R`

This is the core Power Play paper.

It performs:

#### A. Does Power Play increase scoring?

* Compares hammer scoring with vs without PP
* Computes:

  * Average points
  * Big-end rate (≥3)
  * Statistical significance (t-test)

#### B. Counterfactual Modeling

Creates a **no-Power-Play world** by replacing PP ends with baseline hammer scoring.

Produces:

* `Result_No_PP`
* `PP_Delta = Result − Result_No_PP`

Saved as:

```
dfs/ends_with_counterfactual.csv
```

#### C. Game-Level Impact

Computes per-game PP gain:

```
PP_Gain = Σ(Result − Result_No_PP)
```

#### D. End-Level Effectiveness

Analyzes PP effectiveness by:

* End number
* Score context
* PP side (left vs right)

#### E. Usage Strategy

Analyzes:

* When teams use PP
* What score situations trigger PP

---

### 4. Opening Shot Strategy

**Script:** `code/opening_shot_analysis.R`

This studies **Shot 7 (opening) and Shot 8 (hammer response)**.

It analyzes:

#### A. Non-Hammer Opening Shot Effectiveness

For ShotID = 7:

* Execution quality
* End scoring
* Big-end probability
* PP vs non-PP contexts

#### B. Hammer Response Conditional on Opening Shot

For ShotID = 8 given ShotID = 7:

* Shot-pair effectiveness
* End scoring conditional on opening strategy

#### C. Heatmap Visualization

Produces a strategy heatmap:

* Opening shot vs hammer response
* Faceted by Power Play

#### D. Publication Table

Produces a formatted `gt()` table of opening shot effectiveness.

---

## Figures

All figures are saved in `/figures`:

| Figure                    | Description                 |
| ------------------------- | --------------------------- |
| `avg_pp_impact.png`       | Average PP impact per game  |
| `histogram_pp_impact.png` | Distribution of PP gains    |
| `pp_effective_by_end.png` | PP effectiveness by end     |
| `pp_impact_boxplot.png`   | Game-level PP impact        |
| `when_teams_use_pp.png`   | When teams choose to use PP |

---

## Reproducibility

### Requirements

```r
install.packages(c(
  "tidyverse",
  "readr",
  "dplyr",
  "ggplot2",
  "gt"
))
```

### Recommended Workflow

```r
# Step 1: Load raw data
source("code/all_data.R")

# Step 2: Add hammer context
source("code/stones_with_hammer.R")

# Step 3: Build counterfactual dataset & PP analysis
source("code/with_without_PP.R")

# Step 4: Opening shot strategy
source("code/opening_shot_analysis.R")
```

---

## Notes

* `.gitignore` excludes all raw data by default (`*data`)
* Processed datasets live in `/dfs`
* Figures are tracked
* Designed for academic publication and reproducibility

---

## Research Applications

This repository supports:

* Strategy optimization
* Monte Carlo simulation
* Bayesian modeling
* Broadcast analytics
* Coaching decision support
* Tournament preparation
