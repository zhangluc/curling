import torch
from mcts import MCTS
from gamestate import GameState
from bayesian_ev import bayesian_eval_continuous
from prob_table import PROB_TABLE_CUM_DIFF
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt

posterior = torch.load("/Users/brentkong/Documents/curling/weights/unitddpm_<function BaysianRegression at 0x10f9e0ae0>_weights.pt")


frequency_dict = defaultdict(int)
for _ in range(1000):
    result_1 = np.random.choice(list(PROB_TABLE_CUM_DIFF.keys()), p=list(PROB_TABLE_CUM_DIFF.values()))
    result_2 = np.random.choice(list(PROB_TABLE_CUM_DIFF.keys()), p=list(PROB_TABLE_CUM_DIFF.values()))
    round = np.random.choice([i for i in range(1, 9)], p = [0.125 for _ in range(8)])
    used = np.random.choice([True, False], p = [0.5, 0.5])
    state = GameState(
        current_score = {20: result_1, 22: result_2}, # cumulative
        end_number = round,
        root_team = 20,
        hammer_team = 20,
        powerplay_used = {20: False, 22: used},
        ev_model = bayesian_eval_continuous
    )   



    mcts = MCTS(bayesian_eval_continuous, 10000)
    best_action, expected_net_score = mcts.search(state)
    if best_action == "PP":
        frequency_dict[round] += 1


categories = list(frequency_dict.keys())
frequencies = list(frequency_dict.values())

# 4. Create the bar plot
plt.figure(figsize=(8, 6)) # Optional: adjust figure size
plt.bar(categories, frequencies, color='skyblue')

# 5. Add titles and labels
plt.title('Frequency Plot of Items')
plt.xlabel('End')
plt.ylabel('Frequency')

# 6. Display the plot
plt.show()

"""
print("Best Action:", best_action)
print("Expected Net Score After Best Action:", expected_net_score)

hammer = state.hammer_team
opp = [t for t in state.current_score if t != hammer][0]

for a in state.legal_actions():
    ev_h, _ = bayesian_eval_continuous(state.features_for_ev(hammer, a))
    ev_o, _ = bayesian_eval_continuous(state.features_for_ev(opp, a))
    print(a, "EV hammer:", ev_h, "EV opponent:", ev_o, "net:", ev_h - ev_o)
"""

# python run_mcts.py