import torch
from mcts import MCTS
from gamestate import GameState
from bayesian_ev import bayesian_eval_continuous

posterior = torch.load("/Users/brentkong/Documents/curling/weights/unitddpm_<function BaysianRegression at 0x10f9e0ae0>_weights.pt")


state = GameState(
    current_score = {20: 1, 22:3},
    end_number = 3,
    root_team = 20,
    hammer_team = 20,
    powerplay_used = {20: False, 22: False},
)

mcts = MCTS(bayesian_eval_continuous, 800)
best_action, expected_score, uncertainty = mcts.search(state)
print("Best decision:", best_action)
print("Expected points:", expected_score)
print("Uncertainty:", uncertainty)

# python run_mcts.py