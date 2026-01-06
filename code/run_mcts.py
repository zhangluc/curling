import torch
from mcts import MCTS
from gamestate import GameState
from bayesian_ev import bayesian_eval_continuous
from prob_table import PROB_TABLE_END_DIFF
import numpy as np
from copy import deepcopy
import json

matches = 100000

frequency_dict = {end: 0 for end in range(1, 9)}  
frequency_dict["matches"] = matches

wins_dict = {end: 0 for end in range(1, 9)}  
draws_dict = {end: 0 for end in range(1, 9)} 
loss_dict = {end: 0 for end in range(1, 9)}  

hammer_track = {"wins": 0, "draws": 0, "loss": 0}
no_hammer_track = {"wins": 0, "draws": 0, "loss": 0}


pp5_lead_check = {
    "pp6_total": 0,
    "hammer_leading_after_5": 0,
    "hammer_tied_after_5": 0,
    "hammer_trailing_after_5": 0
}

pp5_lead_margin = {
    "total": 0,
    "by_margin": {} 
}

pp6_lead_check = {
    "pp7_total": 0,
    "hammer_leading_after_6": 0,
    "hammer_tied_after_6": 0,
    "hammer_trailing_after_6": 0
}

pp6_lead_margin = {
    "total": 0,
    "by_margin": {} 
}

for _ in range(matches):
    hammer = np.random.choice([1, 2])
    powerplay_used = {1: False, 2: False}
    current_score = {1: 0, 2: 0}
    powerplays_remaining = {1: 1, 2: 1}
    pp_usage = {1: None, 2: None}
    start_hammer = hammer
    root_team = 1

    for end in range(1, 9):
        state = GameState(
            current_score = deepcopy(current_score),
            end_number = end, 
            root_team = root_team,
            hammer_team = hammer,
            powerplay_used = deepcopy(powerplay_used),
            powerplays_remaining = deepcopy(powerplays_remaining)
        )   

        mcts = MCTS(bayesian_eval_continuous, 1000)
        best_action, _ = mcts.search(state)
        
        if best_action == "PP" and powerplays_remaining[root_team] > 0:
            if end == 6:
                pp5_lead_check["pp6_total"] += 1

                lead = int(current_score[root_team] - current_score[3 - root_team])

                if lead > 0:
                    pp5_lead_check["hammer_leading_after_5"] += 1
                elif lead < 0:
                    pp5_lead_check["hammer_trailing_after_5"] += 1
                else:
                    pp5_lead_check["hammer_tied_after_5"] += 1

                pp5_lead_margin["total"] += 1
                pp5_lead_margin["by_margin"][lead] = (
                    pp5_lead_margin["by_margin"].get(lead, 0) + 1
                )

            if end == 7:
                pp6_lead_check["pp7_total"] += 1

                lead = int(current_score[root_team] - current_score[3 - root_team])

                if lead > 0:
                    pp6_lead_check["hammer_leading_after_6"] += 1
                elif lead < 0:
                    pp6_lead_check["hammer_trailing_after_6"] += 1
                else:
                    pp6_lead_check["hammer_tied_after_6"] += 1

                pp6_lead_margin["total"] += 1
                pp6_lead_margin["by_margin"][lead] = (
                    pp6_lead_margin["by_margin"].get(lead, 0) + 1
                )

            pp_usage[root_team] = end
            frequency_dict[end] += 1
            powerplay_used[root_team] = True
            powerplays_remaining[root_team] -= 1

        dist = PROB_TABLE_END_DIFF[best_action][end]
        outcomes = list(dist.keys())
        probs = np.array(list(dist.values()), dtype=float)
        result = np.random.choice(outcomes, p=probs)        

        opp_team = 3 - root_team

        if result > 0:
            current_score[root_team] += result
        elif result < 0:
            current_score[opp_team] += -result
 
        if result  > 0: 
            hammer = 3 - hammer  
        elif result < 0:  
            hammer = hammer  
        else:  
            hammer = 3 - hammer  

    pp_end = pp_usage[root_team]
    if pp_end is not None:
        if current_score[root_team] > current_score[3 - root_team]:
            wins_dict[pp_end] += 1
        elif current_score[root_team] < current_score[3 - root_team]:
            loss_dict[pp_end] += 1
        else:
            draws_dict[pp_end] += 1


    if current_score[start_hammer] > current_score[3 - start_hammer]:
        hammer_track["wins"] += 1
        no_hammer_track["loss"] += 1
    elif current_score[start_hammer] < current_score[3 - start_hammer]:
        hammer_track["loss"] += 1
        no_hammer_track["wins"] += 1
    else:
        hammer_track["draws"] += 1
        no_hammer_track["draws"] += 1
    

hammer_analysis = {
    "hammer_start": hammer_track,
    "no_hammer_start": no_hammer_track
}

with open(f'/Users/brentkong/Documents/curling/figures/simulations/frequency_dict_{matches}_new.json', 'w') as f:
    json.dump([frequency_dict, wins_dict, loss_dict, draws_dict, hammer_analysis, pp5_lead_check, pp5_lead_margin, pp6_lead_check, pp6_lead_margin], f, indent=4) 





