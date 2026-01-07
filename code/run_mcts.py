import torch
from mcts import MCTS
from gamestate import GameState
from bayesian_ev import bayesian_eval_continuous
from prob_table import PROB_TABLE_END_DIFF
import numpy as np
from copy import deepcopy
import json

matches = 100
root_team = 1 

frequency_dict = {end: 0 for end in range(1, 9)}  
frequency_dict["matches"] = matches

wins_dict = {end: 0 for end in range(1, 9)}  
draws_dict = {end: 0 for end in range(1, 9)} 
loss_dict = {end: 0 for end in range(1, 9)}  

hammer_track = {"wins": 0, "draws": 0, "loss": 0}
no_hammer_track = {"wins": 0, "draws": 0, "loss": 0}


pp5_lead_check = {
    "pp6_total": 0,
    "root_leading_after_5": 0,
    "root_tied_after_5": 0,
    "root_trailing_after_5": 0
}

pp5_lead_margin = {
    "total": 0,
    "by_margin": {} 
}

pp6_lead_check = {
    "pp7_total": 0,
    "root_leading_after_6": 0,
    "root_tied_after_6": 0,
    "root_trailing_after_6": 0
}

pp6_lead_margin = {
    "total": 0,
    "by_margin": {} 
}

pp7_lead_check = {
    "pp8_total": 0,
    "root_leading_after_7": 0,
    "root_tied_after_7": 0,
    "root_trailing_after_7": 0
}

pp7_lead_margin = {
    "total": 0,
    "by_margin": {} 
}

for _ in range(matches):
    hammer = np.random.choice([1, 2])
    start_hammer = hammer
    powerplay_used = {1: False, 2: False}
    powerplays_remaining = {1: 1, 2: 1}
    current_score = {1: 0, 2: 0}
    
    root_pp_end = None
    

    for end in range(1, 9):
        acting_team = hammer

        state = GameState(
            current_score = deepcopy(current_score),
            end_number = end, 
            root_team = acting_team,
            hammer_team = hammer,
            powerplay_used = deepcopy(powerplay_used),
            powerplays_remaining = deepcopy(powerplays_remaining)
        )   

        mcts = MCTS(bayesian_eval_continuous, 1000)
        best_action, _ = mcts.search(state)
        
        if best_action == "PP" and powerplays_remaining[acting_team] > 0:
            if acting_team == root_team:
                root_pp_end = end
                frequency_dict[end] += 1

                lead = int(current_score[root_team] - current_score[3 - root_team])
                if end == 6:
                    pp5_lead_check["pp6_total"] += 1
                    if lead > 0:
                        pp5_lead_check["root_leading_after_5"] += 1
                    elif lead < 0:
                        pp5_lead_check["root_trailing_after_5"] += 1
                    else:
                        pp5_lead_check["root_tied_after_5"] += 1

                    pp5_lead_margin["total"] += 1
                    pp5_lead_margin["by_margin"][lead] = pp5_lead_margin["by_margin"].get(lead, 0) + 1     

                if end == 7:
                    pp6_lead_check["pp7_total"] += 1
                    if lead > 0:
                        pp6_lead_check["root_leading_after_6"] += 1
                    elif lead < 0:
                        pp6_lead_check["root_trailing_after_6"] += 1
                    else:
                        pp6_lead_check["root_tied_after_6"] += 1

                    pp6_lead_margin["total"] += 1
                    pp6_lead_margin["by_margin"][lead] = pp6_lead_margin["by_margin"].get(lead, 0) + 1

                if end == 8:
                    pp7_lead_check["pp8_total"] += 1
                    if lead > 0:
                        pp7_lead_check["root_leading_after_7"] += 1
                    elif lead < 0:
                        pp7_lead_check["root_trailing_after_7"] += 1
                    else:
                        pp7_lead_check["root_tied_after_7"] += 1

                    pp7_lead_margin["total"] += 1
                    pp7_lead_margin["by_margin"][lead] = pp7_lead_margin["by_margin"].get(lead, 0) + 1
 
            powerplay_used[acting_team] = True
            powerplays_remaining[acting_team] -= 1

        
        dist = PROB_TABLE_END_DIFF[best_action][end]
        outcomes = list(dist.keys())
        probs = np.array(list(dist.values()), dtype=float)
        result = np.random.choice(outcomes, p=probs)        

        if result > 0:
            current_score[hammer] += result
        elif result < 0:
            current_score[3 - hammer] += -result
 
        if result  > 0: 
            hammer = 3 - hammer  
        elif result < 0:  
            hammer = hammer  
        else:  
            hammer = 3 - hammer  

    if root_pp_end is not None:
        opp = 3 - root_team
        if current_score[root_team] > current_score[opp]:
            wins_dict[root_pp_end] += 1
        elif current_score[root_team] < current_score[opp]:
            loss_dict[root_pp_end] += 1
        else:
            draws_dict[root_pp_end] += 1


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

with open(f'/Users/brentkong/Documents/curling/figures/simulations/frequency_dict_{matches}_both.json', 'w') as f:
    json.dump([frequency_dict, wins_dict, loss_dict, draws_dict, hammer_analysis, pp5_lead_check, pp5_lead_margin, pp6_lead_check, pp6_lead_margin, pp7_lead_check, pp7_lead_margin], f, indent=4) 



