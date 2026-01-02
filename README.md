# Curling AI Simulation with MCTS and Bayesian Models

This project implements a **Monte Carlo Tree Search (MCTS) agent** guided by **Bayesian predictive models** to simulate and evaluate curling games. It includes **training Bayesian models**, **testing their predictive accuracy**, and **running simulations to determine optimal strategic decisions** such as the use of Power Plays.

---

## Table of Contents

* [Overview](#overview)
* [Folder Structure](#folder-structure)
* [Requirements](#requirements)
* [Bayesian Model Training](#bayesian-model-training)
* [EV Evaluation Functions](#ev-evaluation-functions)
* [MCTS + Game Simulation](#mcts--game-simulation)
* [Testing and Metrics](#testing-and-metrics)
* [Output Files](#output-files)

---

## Overview

The project consists of three main components:

1. **Bayesian Regression / Ordered Logistic Models**

   * Trained to predict **expected end scores (EV)** based on game features:

     * Hammer possession
     * Power Play usage
     * Current end number
     * Previous score difference
   * Supports both **continuous regression** and **ordinal scoring (OrderedLogistic)**.

2. **EV Evaluation Functions**

   * `bayesian_eval_continuous(features, posterior)`
   * `bayesian_eval_ordered(features, posterior)`
   * These functions compute the **expected value (EV)** and **uncertainty** for a given state.

3. **Monte Carlo Tree Search (MCTS) Simulation**

   * Uses EV predictions to guide tree search.
   * Simulates multiple possible end outcomes using **probabilistic score tables (`PROB_TABLE_END_DIFF`)**.
   * Decides on actions such as **Power Play usage** to maximize win probability.

---

## Folder Structure

```
project/
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
│   ├── data_processing.ipynb
│   ├── model_results
│   │   ├── Model_Results_Continuous.csv
│   │   └── Model_Results_Ordered.csv
│   ├── processed_data
│   │   ├── bayesian_training.csv
│   │   ├── ends_processed.csv
│   │   ├── games_processed.csv
│   │   └── stones_processed.csv
│   ├── train_test_data
│   │   ├── test_df.csv
│   │   └── train_df.csv
│   └── train_test_split.ipynb
│
├── figures
│   ├── analysis
│   │   └── analysis.csv
│   ├── analysis.py
│   ├── graphs
│   │   ├── Frequency_End.png
│   │   ├── hammer_vs_no_hammer_pie.png
│   │   └── Win_Draw_Per_End.png
│   └── simulations
│       └── frequency_dict_10000.json
│
├── weights
│   ├── testing_weights
│   │   ├── unitddpm_<function BaysianRegression ...>_weights.pt
│   │   └── unitddpm_<function OrderedLogistic ...>_weights.pt
│   └── unitddpm_<function BaysianRegression ...>_weights.pt
│
├── README.md
├── requirements.txt
└── useful_commands.md
```

---
### Requirements

This project requires Python 3.13+ and the following packages:

* **PyTorch** (`torch`): Core library for tensor computations and modeling. Used for Bayesian regression, Ordered Logistic models, and MCTS evaluation.
* **Pyro** (`pyro-ppl`): Probabilistic programming library built on PyTorch. Used for Bayesian model definition and inference.
* **Pandas** (`pandas`): Data manipulation and preprocessing, including reading CSVs for training and testing.
* **Matplotlib** (`matplotlib`): Visualization of results, simulation outputs, and graphs.
* **scikit-learn** (`sklearn`): Evaluation metrics like RMSE, MAE, and R², and optional preprocessing utilities.

You can install all dependencies via pip:

```bash
pip install -r requirements.txt
```
---

## Bayesian Model Training

Two models are trained using Pyro + NUTS (Hamiltonian Monte Carlo):

1. **Ordered Logistic Model**

   * Predicts discrete outcomes (score differences 0–6).
   * Uses `raw_cutpoints` transformed to ensure monotonicity with `softplus` + `cumsum`.

2. **Continuous Bayesian Regression**

   * Predicts continuous expected scores.
   * Estimates mean (`mu`) and uncertainty (`sigma`).

Training script:

```bash
python train_bayesian_model.py
```

* Saves posterior weights as `.pt` files.
* Posterior weights are later used for EV evaluation.

---

## EV Evaluation Functions

* `bayesian_eval_continuous(features, posterior)` → returns `(mean, std)`
* `bayesian_eval_ordered(features, posterior)` → returns `(mean, std)`

Used by both **MCTS** and testing scripts to calculate expected end outcomes.

---

## MCTS + Game Simulation

**MCTSNode** and **MCTS** classes implement Monte Carlo Tree Search:

* Each node represents a game state.
* **Expansion:** Adds a new node for unexplored legal action.
* **Simulation:** Plays out random end outcomes using `PROB_TABLE_END_DIFF`.
* **Backpropagation:** Updates visit counts and rewards.

**GameState** class:

* Tracks `current_score`, `end_number`, `hammer_team`, `powerplay_used`, and `powerplays_remaining`.
* Provides:

  * Legal actions
  * Feature vectors for EV evaluation
  * Next state after an action
  * Probabilistic end score sampling

---

## Testing and Metrics

* `test.py` runs predictions for both **continuous** and **ordered** models.
* Metrics include:

  * **RMSE:** Root Mean Squared Error
  * **MAE:** Mean Absolute Error
  * **Bias:** Average over/underprediction
  * **R²:** Coefficient of determination

Example usage:

```bash
python test.py
```

---

## Output Files

1. **Model results CSVs**

* `Model_Results_Continuous.csv`
* `Model_Results_Ordered.csv`

  ```
  RMSE, MAE, Bias, R2
  0.93, 0.72, 0.04, 0.16
  ```

2. **Simulation JSONs**

* `frequency_dict_<matches>.json`
  Contains:

  * Power Play frequency per end
  * Wins, draws, losses per end
  * Hammer vs. No Hammer analysis

---

## Notes

* **Standard deviation (uncertainty)** from Bayesian models is tracked but not strictly used for EV decisions.
* Low RMSE (~0.93) is acceptable for the 0–6 score target.
* MCTS uses **EV differences** and a logistic function to approximate **win probability** per end.
* Power Play decisions are simulated **strategically** using this setup.

---

## References

* Pyro: [https://pyro.ai](https://pyro.ai)
* MCTS: Browne et al., *A Survey of Monte Carlo Tree Search Methods*, 2012
