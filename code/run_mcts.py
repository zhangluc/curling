import torch
from mcts import MCTS
from gamestate import GameState
from bayesian_ev import bayesian_eval_continuous

posterior = torch.load("/Users/brentkong/Documents/curling/weights/unitddpm_<function BaysianRegression at 0x10f9e0ae0>_weights.pt")


state = GameState(
    current_score = {20: 0, 22: 2},
    end_number = 1,
    root_team = 20,
    hammer_team = 20,
    powerplay_used = {20: False, 22: False},
)

mcts = MCTS(bayesian_eval_continuous, 3000)
best_action, expected_net_score = mcts.search(state)
print("Best Action:", best_action)
print("Expected Net Score After Best Action:", expected_net_score)

hammer = state.hammer_team
opp = [t for t in state.current_score if t != hammer][0]

for a in state.legal_actions():
    ev_h, _ = bayesian_eval_continuous(state.features_for_ev(a, hammer, opp, True))
    ev_o, _ = bayesian_eval_continuous(state.features_for_ev(a, hammer, opp, False))
    print(a, "EV hammer:", ev_h, "EV opponent:", ev_o, "net:", ev_h - ev_o)


# python run_mcts.py