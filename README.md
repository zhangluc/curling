# Curling AI Simulation with MCTS and Bayesian Regression

This project implements a **Monte Carlo Tree Search (MCTS) agent** guided by a **Bayesian regression model** to simulate and evaluate curling games. It includes **training a Bayesian model**, **testing its predictive accuracy**, and **running simulations to determine optimal strategic decisions** such as Power Play timing.

---

## Table of Contents

* [Installation](#installation)
* [Project Overview](#project-overview)
* [Folder Structure](#folder-structure)
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
│   ├── train_test_split.ipynb
│   │
│   ├── model_results
│   │   └── Model_Results_Continuous.csv
│   │
│   ├── processed_data
│   │   ├── bayesian_training.csv
│   │   ├── ends_processed.csv
│   │   ├── ends_with_counterfactual.csv
│   │   ├── games_processed.csv
│   │   └── stones_processed.csv
│   │
│   └── train_test_data
│       ├── test_df.csv
│       └── train_df.csv
│
├── figures
│   ├── analysis
│   ├── graphs
│   ├── simulations
│   ├── analysis.py
│   ├── exploratory_graphs.py
│   ├── graphs.py
│   └── pp_effect.py
│
├── requirements.txt
├── useful_commands.md
└── weights
```

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
