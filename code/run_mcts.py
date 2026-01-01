import torch
from mcts import MCTS
from gamestate import GameState
from bayesian_ev import bayesian_eval_continuous
from prob_table import PROB_TABLE_END_DIFF
import numpy as np
from copy import deepcopy
import json

posterior = torch.load("/Users/brentkong/Documents/curling/weights/unitddpm_<function BaysianRegression at 0x10f9e0ae0>_weights.pt")

matches = 10000
frequency_dict = {end: 0 for end in range(1, 9)}  
frequency_dict["matches"] = matches
wins_dict = {end: 0 for end in range(1, 9)}  
draws_dict = {end: 0 for end in range(1, 9)} 
loss_dict = {end: 0 for end in range(1, 9)}  

wins_hammer, wins_no_hammer = 0, 0
draws_hammer, draws_no_hammer = 0, 0
loss_hammer, loss_no_hammer  = 0, 0

for _ in range(matches):
    hammer = np.random.choice([1, 2])
    powerplay_used = {1: False, 2: False}
    current_score = {1: 0, 2: 0}
    powerplays_remaining = {1: 1, 2: 1}
    powerplay_end = None
    root_has_hammer = (hammer == 1)
    for end in range(1, 9):
        opp = [t for t in current_score if t != hammer][0]
        state = GameState(
            current_score = deepcopy(current_score),
            end_number = end, 
            root_team = 1,
            hammer_team = hammer,
            powerplay_used = deepcopy(powerplay_used),
            powerplays_remaining = deepcopy(powerplays_remaining)
        )   

        mcts = MCTS(bayesian_eval_continuous, 5000)
        best_action, _ = mcts.search(state)

        if best_action == "PP" and hammer == 1:
            frequency_dict[end] += 1
            powerplay_end = end

        dist = PROB_TABLE_END_DIFF[best_action][end]
        outcomes = list(dist.keys())
        probs = np.array(list(dist.values()), dtype=float)
        result = np.random.choice(outcomes, p=probs)        

        if result > 0:
            current_score[hammer] += result
        elif result < 0:
            current_score[opp] += -result

        if best_action == "PP":
            powerplay_used[hammer] = True
            powerplays_remaining[hammer] -= 1

        scored = result  

        if scored > 0: 
            hammer = 3 - hammer  
        elif scored < 0:  
            hammer = hammer  
        else:  
            hammer = 3 - hammer  

    if powerplay_end is not None:
        if current_score[1] > current_score[2]:
            wins_dict[powerplay_end] += 1
        elif current_score[1] < current_score[2]:
            loss_dict[powerplay_end] += 1
        else:
            draws_dict[powerplay_end] += 1
    
    if root_has_hammer:
        if current_score[1] > current_score[2]:
            wins_hammer += 1
        elif current_score[1] < current_score[2]:
            loss_hammer += 1
        else:
            draws_hammer += 1
    else:
        if current_score[1] > current_score[2]:
            wins_no_hammer += 1
        elif current_score[1] < current_score[2]:
            loss_no_hammer += 1
        else:
            draws_no_hammer += 1

hammer_analysis = {
    "hammer_start": {"wins": wins_hammer, "draws": draws_hammer, "losses": loss_hammer, "matches": sum([wins_hammer, draws_hammer, loss_hammer])},
    "no_hammer_start": {"wins": wins_no_hammer, "draws": draws_no_hammer, "losses": loss_no_hammer, "matches": sum([wins_no_hammer, draws_no_hammer, loss_no_hammer])}
}

with open(f'/Users/brentkong/Documents/curling/figures/simulations/frequency_dict_{matches}.json', 'w') as f:
    json.dump([frequency_dict, wins_dict, loss_dict, draws_dict, hammer_analysis], f, indent=4) 





