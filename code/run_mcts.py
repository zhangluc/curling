import json
import numpy as np
from mcts import MCTS
from pathlib import Path
from copy import deepcopy
from gamestate import GameState
from prob_table import PROB_TABLE_END_DIFF
from bayesian_ev import bayesian_eval_continuous

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAVE_DIR = PROJECT_ROOT / "figures" / "simulations"

matches = 1000
root_team = 1 

pp_calls_dict = {end: 0 for end in range(1, 9)}
pp_calls_dict["matches"] = matches

pp_wins_dict  = {end: 0 for end in range(1, 9)}
pp_draws_dict = {end: 0 for end in range(1, 9)}
pp_loss_dict  = {end: 0 for end in range(1, 9)}

hammer_track = {"wins": 0, "draws": 0, "loss": 0}
no_hammer_track = {"wins": 0, "draws": 0, "loss": 0}


pp5_lead_check = {
    "pp6_total": 0,
    "caller_leading_after_5": 0,
    "caller_tied_after_5": 0,
    "caller_trailing_after_5": 0
}

pp5_lead_margin = {
    "total": 0,
    "by_margin": {} 
}

pp6_lead_check = {
    "pp7_total": 0,
    "caller_leading_after_6": 0,
    "caller_tied_after_6": 0,
    "caller_trailing_after_6": 0
}

pp6_lead_margin = {
    "total": 0,
    "by_margin": {} 
}

pp7_lead_check = {
    "pp8_total": 0,
    "caller_leading_after_7": 0,
    "caller_tied_after_7": 0,
    "caller_trailing_after_7": 0
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
    
    pp_end_by_team = {1: None, 2: None}
    

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
        
        if best_action == "PP" and powerplays_remaining[acting_team] <= 0:
            best_action = "NO_PP"

        if best_action == "PP" and powerplays_remaining[acting_team] > 0:
            if pp_end_by_team[acting_team] is None:
                pp_end_by_team[acting_team] = end
                pp_calls_dict[end] += 1

                lead = int(current_score[acting_team] - current_score[3 - acting_team])

                if end == 6:
                    pp5_lead_check["pp6_total"] += 1
                    if lead > 0:
                        pp5_lead_check["caller_leading_after_5"] += 1
                    elif lead < 0:
                        pp5_lead_check["caller_trailing_after_5"] += 1
                    else:
                        pp5_lead_check["caller_tied_after_5"] += 1

                    pp5_lead_margin["total"] += 1
                    pp5_lead_margin["by_margin"][lead] = pp5_lead_margin["by_margin"].get(lead, 0) + 1

                if end == 7:
                    pp6_lead_check["pp7_total"] += 1
                    if lead > 0:
                        pp6_lead_check["caller_leading_after_6"] += 1
                    elif lead < 0:
                        pp6_lead_check["caller_trailing_after_6"] += 1
                    else:
                        pp6_lead_check["caller_tied_after_6"] += 1

                    pp6_lead_margin["total"] += 1
                    pp6_lead_margin["by_margin"][lead] = pp6_lead_margin["by_margin"].get(lead, 0) + 1

                if end == 8:
                    pp7_lead_check["pp8_total"] += 1
                    if lead > 0:
                        pp7_lead_check["caller_leading_after_7"] += 1
                    elif lead < 0:
                        pp7_lead_check["caller_trailing_after_7"] += 1
                    else:
                        pp7_lead_check["caller_tied_after_7"] += 1

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

    for team, pp_end in pp_end_by_team.items():
        if pp_end is None:
            continue
        opp = 3 - team
        if current_score[team] > current_score[opp]:
            pp_wins_dict[pp_end] += 1
        elif current_score[team] < current_score[opp]:
            pp_loss_dict[pp_end] += 1
        else:
            pp_draws_dict[pp_end] += 1



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

with open(SAVE_DIR / f'frequency_dict_{matches}.json', 'w') as f:
    json.dump([
        pp_calls_dict, pp_wins_dict, pp_loss_dict, pp_draws_dict,
        hammer_analysis,
        pp5_lead_check, pp5_lead_margin,
        pp6_lead_check, pp6_lead_margin,
        pp7_lead_check, pp7_lead_margin
    ], f, indent=4)



