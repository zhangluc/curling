# Curling AI Simulation with MCTS and Bayesian Regression

This project implements a **Monte Carlo Tree Search (MCTS) agent** guided by a **Bayesian regression model** to simulate and evaluate curling games. It includes **training a Bayesian model**, **testing its predictive accuracy**, and **running simulations to determine optimal strategic decisions** such as Power Play timing.

---

## Table of Contents

* [Installation](#installation)
* [Project Overview](#project-overview)
* [Folder Structure](#folder-structure)
* [Code Reference: File-by-File Overview](#code-reference-file-by-file-overview)
* [Data Processing & Train-Test Split](#data-processing--train-test-split)
* [Bayesian Model Training](#bayesian-model-training)
* [EV Evaluation Function](#ev-evaluation-function)
* [MCTS Game Simulation](#mcts-game-simulation)
* [Testing and Metrics](#testing-and-metrics)
* [Output Files](#output-files)
* [Notes](#notes)
* [References](#references)

---

# Installation

## Requirements

* Python **3.13+**
* pip

---

## Create a Virtual Environment (Required)

From the project root directory:

```bash
python3 -m venv venv
```

### Activate the Virtual Environment

**macOS / Linux**

```bash
source venv/bin/activate
```

**Windows (PowerShell)**

```powershell
venv\Scripts\Activate.ps1
```

---

## Install Dependencies

With the virtual environment activated:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Required packages include:

* **torch** – Bayesian regression model
* **pyro-ppl** – probabilistic inference (NUTS)
* **pandas** – data processing
* **matplotlib** – visualization
* **scikit-learn** – evaluation metrics

---

## Deactivate When Finished

```bash
deactivate
```

> Note: The virtual environment folder (`venv/`) should not be committed to version control. Add it to `.gitignore`.

---

# Project Overview

The project consists of three main components:

### 1. Bayesian Regression Model

Predicts expected end score (EV) from game features:

* Hammer possession
* Power Play usage
* End number
* Previous score difference

Provides both expected value and uncertainty.

---

### 2. EV Evaluation Function

Computes expected value for a given game state using posterior samples.

---

### 3. Monte Carlo Tree Search (MCTS)

* Uses Bayesian EV predictions to guide tree search
* Simulates stochastic scoring outcomes using empirical score tables
* Learns optimal Power Play timing policies

---

# Folder Structure

```
curling/
├── code
│   ├── bayesian_ev.py
│   ├── gamestate.py
│   ├── mcts.py
│   ├── prob_table.py
│   ├── run_mcts.py
│   ├── test.py
│   └── train_bayesian_model.py
│
├── data_processing
│   ├── data_analysis.ipynb
│   ├── data_processing.ipynb
│   ├── model_results
│   │   └── Model_Results_Continuous.csv
│   ├── processed_data
│   │   ├── bayesian_training.csv
│   │   ├── ends_processed.csv
│   │   ├── ends_with_counterfactual.csv
│   │   ├── games_processed.csv
│   │   └── stones_processed.csv
│   ├── train_test_data
│   │   ├── test_df.csv
│   │   └── train_df.csv
│   └── train_test_split.ipynb
│
├── figures
│   ├── analysis
│   │   ├── data_analysis
│   │   │   ├── hammer_response.csv
│   │   │   ├── opening_shot.csv
│   │   │   ├── powerplay_end_summary.csv
│   │   │   └── powerplay_entry_margin_stats_6_8.csv
│   │   ├── end_frequency_combined
│   │   │   ├── end_1_frequency_combined.png
│   │   │   ├── end_2_frequency_combined.png
│   │   │   ├── end_3_frequency_combined.png
│   │   │   ├── end_4_frequency_combined.png
│   │   │   ├── end_5_frequency_combined.png
│   │   │   ├── end_6_frequency_combined.png
│   │   │   ├── end_7_frequency_combined.png
│   │   │   └── end_8_frequency_combined.png
│   │   └── simulation_statistics
│   │       ├── analysis_100000_both.csv
│   │       └── analysis_margin100000_both.csv
│   ├── analysis.py
│   ├── exploratory_graphs.py
│   ├── graphs
│   │   ├── distribution_pp_tail.png
│   │   ├── frequency_end_100000.png
│   │   ├── pp_effectiveness.png
│   │   ├── win_after_5_100000.png
│   │   ├── win_after_6_100000.png
│   │   ├── win_after_7_100000.png
│   │   └── win_draw_100000.png
│   ├── graphs.py
│   ├── shot_effect.py
│   └── simulations
│       └── frequency_dict_100000.json
│
├── requirements.txt
└── weights
    ├── testing_weights
    │   └── unitddpm_BaysianRegression_20260111_193054_82cf67d5_weights.pt
    └── unitddpm_BaysianRegression_20260111_193019_830f987c_weights.pt
```
---

# Code Reference: File-by-File Overview

This section describes the purpose and functionality of each core Python file in the project.

---

## Core Simulation & Modeling Code (`/code`)

---

### `train_bayesian_model.py`

**Purpose:**
Trains the Bayesian regression model used to estimate expected end score.

**What it does:**

* Loads `train_df.csv` from `data_processing/train_test_data/`
* Builds a Bayesian linear regression model in Pyro
* Uses NUTS (Hamiltonian Monte Carlo) for posterior inference
* Learns distributions over:

  * Regression weights
  * Bias term
  * Observation noise
* Saves posterior samples to `weights/`

**Role in pipeline:**
Provides the trained probabilistic model used by the EV evaluation function and MCTS.

---

### `bayesian_ev.py`

**Purpose:**
Implements the Expected Value (EV) evaluation function.

**What it does:**

* Loads posterior samples from `weights/`
* Computes posterior predictive distributions for a given game state
* Returns:

  * Expected end score (mean)
  * Predictive uncertainty (standard deviation)

**Role in pipeline:**
Acts as the evaluation function for MCTS and for offline model testing.

---

### `gamestate.py`

**Purpose:**
Defines the curling game environment and state transition dynamics.

**What it does:**

* Represents a full curling match state:

  * Current score
  * Hammer possession
  * End number
  * Power Play availability for both teams
* Generates legal actions:

  * Call Power Play
  * Do not call Power Play
* Advances the game forward by simulating an end
* Samples stochastic scoring outcomes from `PROB_TABLE_END_DIFF`

**Role in pipeline:**
Provides the environment model used by MCTS for simulation and rollout.

---

### `prob_table.py`

**Purpose:**
Defines the empirical scoring model.

**What it does:**

* Stores `PROB_TABLE_END_DIFF`
* This table represents the empirical probability distribution over:

  * End score differentials (−6 to +6)
  * Conditioned on:

    * Hammer possession
    * Power Play usage

**Role in pipeline:**
Acts as the stochastic transition model for the simulator.

---

### `mcts.py`

**Purpose:**
Implements the Monte Carlo Tree Search algorithm.

**What it does:**

* Implements UCT (Upper Confidence Trees) for action selection
* Uses Bayesian EV estimates to evaluate leaf nodes
* Handles:

  * Selection
  * Expansion
  * Simulation (rollouts using `GameState`)
  * Backpropagation of EV-based rewards
* Learns an optimal Power Play timing policy over a full match horizon

**Role in pipeline:**
Core decision-making engine of the project.

---

### `run_mcts.py`

**Purpose:**
Runs large-scale curling match simulations using the MCTS agent.

**What it does:**

* Randomly initializes match states
* Runs a full MCTS search for each game
* Simulates thousands of matches
* Tracks:

  * Power Play usage frequency by end
  * Win/draw/loss rates
  * Hammer advantage statistics
* Saves aggregate statistics to JSON files

**Outputs:**

* `frequency_dict_<matches>.json`
* Win/draw/loss distributions
* Hammer vs non-hammer performance

---

### `test.py`

**Purpose:**
Evaluates the Bayesian regression model on held-out test data.

**What it does:**

* Loads `test_df.csv`
* Runs posterior predictive inference
* Computes evaluation metrics:

  * RMSE
  * MAE
  * Bias
  * R²
* Saves results to CSV

**Output:**

```
data_processing/model_results/Model_Results_Continuous.csv
```
---

# Code Reference: File-by-File Overview

This section describes the purpose and functionality of each core Python file in the project.

---

## Core Simulation & Modeling Code (`/code`)

---

### `train_bayesian_model.py`

**Purpose:**
Trains the Bayesian regression model used to estimate expected end score.

**What it does:**

* Loads `train_df.csv` from `data_processing/train_test_data/`
* Builds a Bayesian linear regression model in Pyro
* Uses NUTS (Hamiltonian Monte Carlo) for posterior inference
* Learns distributions over:

  * Regression weights
  * Bias term
  * Observation noise
* Saves posterior samples to `weights/`

**Role in pipeline:**
Provides the trained probabilistic model used by the EV evaluation function and MCTS.

---

### `bayesian_ev.py`

**Purpose:**
Implements the Expected Value (EV) evaluation function.

**What it does:**

* Loads posterior samples from `weights/`
* Computes posterior predictive distributions for a given game state
* Returns:

  * Expected end score (mean)
  * Predictive uncertainty (standard deviation)

**Role in pipeline:**
Acts as the evaluation function for MCTS and for offline model testing.

---

### `gamestate.py`

**Purpose:**
Defines the curling game environment and state transition dynamics.

**What it does:**

* Represents a full curling match state:

  * Current score
  * Hammer possession
  * End number
  * Power Play availability for both teams
* Generates legal actions:

  * Call Power Play
  * Do not call Power Play
* Advances the game forward by simulating an end
* Samples stochastic scoring outcomes from `PROB_TABLE_END_DIFF`

**Role in pipeline:**
Provides the environment model used by MCTS for simulation and rollout.

---

### `prob_table.py`

**Purpose:**
Defines the empirical scoring model.

**What it does:**

* Stores `PROB_TABLE_END_DIFF`
* This table represents the empirical probability distribution over:

  * End score differentials (−6 to +6)
  * Conditioned on:

    * Hammer possession
    * Power Play usage

**Role in pipeline:**
Acts as the stochastic transition model for the simulator.

---

### `mcts.py`

**Purpose:**
Implements the Monte Carlo Tree Search algorithm.

**What it does:**

* Implements UCT (Upper Confidence Trees) for action selection
* Uses Bayesian EV estimates to evaluate leaf nodes
* Handles:

  * Selection
  * Expansion
  * Simulation (rollouts using `GameState`)
  * Backpropagation of EV-based rewards
* Learns an optimal Power Play timing policy over a full match horizon

**Role in pipeline:**
Core decision-making engine of the project.

---

### `run_mcts.py`

**Purpose:**
Runs large-scale curling match simulations using the MCTS agent.

**What it does:**

* Randomly initializes match states
* Runs a full MCTS search for each game
* Simulates thousands of matches
* Tracks:

  * Power Play usage frequency by end
  * Win/draw/loss rates
  * Hammer advantage statistics
* Saves aggregate statistics to JSON files

**Outputs:**

* `frequency_dict_<matches>.json`
* Win/draw/loss distributions
* Hammer vs non-hammer performance

---

### `test.py`

**Purpose:**
Evaluates the Bayesian regression model on held-out test data.

**What it does:**

* Loads `test_df.csv`
* Runs posterior predictive inference
* Computes evaluation metrics:

  * RMSE
  * MAE
  * Bias
  * R²
* Saves results to CSV

**Output:**

```
data_processing/model_results/Model_Results_Continuous.csv
```

---

## Data & Analysis Scripts (`/figures`)

---

### `analysis.py`

**Purpose:**
Generates summary statistics and tables used in reporting.

**What it does:**

* Loads processed datasets and simulation outputs
* Computes:

  * End-level scoring distributions
  * Power Play frequency statistics
  * Margin distributions
* Produces publication-ready tables

**Role in pipeline:**
Statistical analysis layer for results.

---

### `graphs.py`

**Purpose:**
Generates all publication-quality figures.

**What it does:**

* Creates:

  * End frequency bar charts
  * Win/draw curves
  * Margin distributions
  * Correlation heatmaps
* Saves figures to `/figures/graphs/` and `/figures/simulations/`

**Role in pipeline:**
Visualization and reporting.

---

### `exploratory_graphs.py`

**Purpose:**
Exploratory data analysis and sanity checking.

**What it does:**

* Visualizes:

  * End score distributions
  * Hammer effects
  * Power Play effects
* Used during dataset understanding and validation

**Role in pipeline:**
EDA and validation.

---

### `pp_effect.py`

**Purpose:**
Analyzes the empirical effect of Power Play usage.

**What it does:**

* Compares scoring with and without Power Play
* Computes:

  * Mean score differences
  * Win rate shifts
  * Margin distributions

**Role in pipeline:**
Empirical grounding for simulation assumptions.

---

## Notebooks (`/data_processing`)

---

### `data_processing.ipynb`

**Purpose:**
Transforms raw Curling Canada shot-level data into model-ready datasets.

**What it does:**

* Cleans and normalizes raw data
* Aggregates:

  * Shot-level → end-level
  * End-level → game-level
* Creates:

  * `ends_processed.csv`
  * `games_processed.csv`
  * `stones_processed.csv`
  * `bayesian_training.csv`

**Role in pipeline:**
Primary data engineering stage.

---

### `train_test_split.ipynb`

**Purpose:**
Creates the training and evaluation datasets.

**What it does:**

* Loads `bayesian_training.csv`
* Performs an 80–20 train-test split
* Saves:

  * `train_df.csv`
  * `test_df.csv`

**Role in pipeline:**
Model evaluation pipeline.

---

### `data_analysis.ipynb`

**Purpose:**
Exploratory analysis and validation notebook.

**What it does:**

* Explores distributions of:

  * End scores
  * Margins
  * Hammer advantage
  * Power Play usage
* Validates modeling assumptions used by MCTS and Bayesian regression

**Role in pipeline:**
Research validation and sanity checking.

---

## Weights (`/weights`)

**Purpose:**
Stores trained Bayesian posterior samples.

**Contents:**

* Regression coefficients
* Bias terms
* Noise variance
* Used by `bayesian_ev.py` and MCTS

---

## Summary

| File                      | Role                      |
| ------------------------- | ------------------------- |
| `train_bayesian_model.py` | Bayesian model training   |
| `bayesian_ev.py`          | Expected value prediction |
| `gamestate.py`            | Curling environment       |
| `prob_table.py`           | Empirical scoring model   |
| `mcts.py`                 | Monte Carlo Tree Search   |
| `run_mcts.py`             | Simulation runner         |
| `test.py`                 | Model evaluation          |
| `analysis.py`             | Statistical analysis      |
| `graphs.py`               | Figure generation         |
| `exploratory_graphs.py`   | Exploratory analysis      |
| `pp_effect.py`            | Power Play impact study   |
| `data_processing.ipynb`   | Data engineering          |
| `train_test_split.ipynb`  | Train-test split          |
| `data_analysis.ipynb`     | Validation & EDA          |
---

## Data & Analysis Scripts (`/figures`)

---

### `analysis.py`

**Purpose:**
Generates summary statistics and tables used in reporting.

**What it does:**

* Loads processed datasets and simulation outputs
* Computes:

  * End-level scoring distributions
  * Power Play frequency statistics
  * Margin distributions
* Produces publication-ready tables

**Role in pipeline:**
Statistical analysis layer for results.

---

### `graphs.py`

**Purpose:**
Generates all publication-quality figures.

**What it does:**

* Creates:

  * End frequency bar charts
  * Win/draw curves
  * Margin distributions
  * Correlation heatmaps
* Saves figures to `/figures/graphs/` and `/figures/simulations/`

**Role in pipeline:**
Visualization and reporting.

---

### `exploratory_graphs.py`

**Purpose:**
Exploratory data analysis and sanity checking.

**What it does:**

* Visualizes:

  * End score distributions
  * Hammer effects
  * Power Play effects
* Used during dataset understanding and validation

**Role in pipeline:**
EDA and validation.

---
### `shot_effect.py`

**Purpose:**
Analyzes the empirical impact of opening-shot strategy and hammer response under Power Play.

**What it does:**

* Evaluates non-hammer opening shots and hammer response shots
* Compares outcomes with and without Power Play
* Computes:

  * Execution quality
  * End-level scoring
  * Big-end frequency

**Role in pipeline:**
Empirical grounding for early-end tactical dynamics and Power Play modeling assumptions.
---

## Notebooks (`/data_processing`)

---

### `data_processing.ipynb`

**Purpose:**
Transforms raw Curling Canada shot-level data into model-ready datasets.

**What it does:**

* Cleans and normalizes raw data
* Aggregates:

  * Shot-level → end-level
  * End-level → game-level
* Creates:

  * `ends_processed.csv`
  * `games_processed.csv`
  * `stones_processed.csv`
  * `bayesian_training.csv`

**Role in pipeline:**
Primary data engineering stage.

---

### `train_test_split.ipynb`

**Purpose:**
Creates the training and evaluation datasets.

**What it does:**

* Loads `bayesian_training.csv`
* Performs an 80–20 train-test split
* Saves:

  * `train_df.csv`
  * `test_df.csv`

**Role in pipeline:**
Model evaluation pipeline.

---

### `data_analysis.ipynb`

**Purpose:**
Exploratory analysis and validation notebook.

**What it does:**

* Explores distributions of:

  * End scores
  * Margins
  * Hammer advantage
  * Power Play usage
* Validates modeling assumptions used by MCTS and Bayesian regression

**Role in pipeline:**
Research validation and sanity checking.

---

## Weights (`/weights`)

**Purpose:**
Stores trained Bayesian posterior samples.

**Contents:**

* Regression coefficients
* Bias terms
* Noise variance
* Used by `bayesian_ev.py` and MCTS

---

## Summary

| File                      | Role                      |
| ------------------------- | ------------------------- |
| `train_bayesian_model.py` | Bayesian model training   |
| `bayesian_ev.py`          | Expected value prediction |
| `gamestate.py`            | Curling environment       |
| `prob_table.py`           | Empirical scoring model   |
| `mcts.py`                 | Monte Carlo Tree Search   |
| `run_mcts.py`             | Simulation runner         |
| `test.py`                 | Model evaluation          |
| `analysis.py`             | Statistical analysis      |
| `graphs.py`               | Figure generation         |
| `exploratory_graphs.py`   | Exploratory analysis      |
| `shot_effect.py`          | Shot type impact study    |
| `data_processing.ipynb`   | Data engineering          |
| `train_test_split.ipynb`  | Train-test split          |
| `data_analysis.ipynb`     | Validation & EDA          |
---

# Data Processing & Train-Test Split

Raw Curling Canada shot-level data is processed into end-level and game-level datasets using:

```bash
jupyter notebook data_processing/data_processing.ipynb
```

The Bayesian training dataset is then split into training and testing sets using an **80–20 split**:

```bash
jupyter notebook data_processing/train_test_split.ipynb
```

This produces:

```
data_processing/train_test_data/train_df.csv
data_processing/train_test_data/test_df.csv
```

---

# Bayesian Model Training

A **Bayesian linear regression model** is trained using Pyro + NUTS (Hamiltonian Monte Carlo).

The model:

* Predicts expected end score (real-valued)
* Learns posterior distributions over weights and noise
* Provides predictive uncertainty

Train the model with:

```bash
python train_bayesian_model.py
```

This:

* Loads `train_df.csv`
* Runs Bayesian inference
* Saves posterior weights to `weights/`

---

# EV Evaluation Function

Implemented in `bayesian_ev.py`:

```python
bayesian_eval_continuous(features, posterior) -> (mean, std)
```

Returns:

* **Expected value (EV)**
* **Predictive uncertainty**

Used by both MCTS and evaluation scripts.

---

# MCTS Game Simulation

Monte Carlo Tree Search is implemented in `mcts.py` and `gamestate.py`.

### Key Components

**GameState**

* Tracks score, hammer, end number, and remaining Power Plays
* Generates legal actions
* Samples stochastic end outcomes using `PROB_TABLE_END_DIFF`

**MCTS**

* Selection via UCT
* Expansion of new actions
* Simulation using probabilistic score tables
* Backpropagation of EV-based rewards

Run full simulations with:

```bash
python run_mcts.py
```

---

# Testing and Metrics

Model evaluation is performed on the held-out 20% test set.

Run evaluation:

```bash
python test.py
```

Metrics reported:

* **RMSE** – Root Mean Squared Error
* **MAE** – Mean Absolute Error
* **Bias** – Mean prediction error
* **R²** – Coefficient of determination

Results are saved to:

```
data_processing/model_results/Model_Results_Continuous.csv
```

---

# Output Files

### Model Metrics

`Model_Results_Continuous.csv`

```
RMSE, MAE, Bias, R2
0.91, 0.71, 0.06, 0.14
```

---

### Simulation Results

`frequency_dict_<matches>.json`

Contains:

* Power Play frequency per end
* Win/draw/loss rates
* Hammer advantage analysis

---

# Notes

* Bayesian uncertainty is tracked for stability
* MCTS uses EV differences with a logistic transformation to approximate win probability
* Power Play timing is learned strategically rather than hard-coded
* Low RMSE (< 1 point) is acceptable for a 0–6 scoring range

---

# References

* Pyro: [https://pyro.ai](https://pyro.ai)
* Browne et al., *A Survey of Monte Carlo Tree Search Methods*, 2012
