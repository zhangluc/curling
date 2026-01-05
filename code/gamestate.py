import numpy as np
from prob_table import PROB_TABLE_END_DIFF

class GameState:
    def __init__(self, current_score, end_number, root_team, hammer_team, powerplay_used, max_ends=8, powerplays_remaining = None, prev_end_diff=0):
        self.current_score = current_score  # dict: {team1: score1, team2: score2}
        self.end_number = end_number
        self.root_team = root_team
        self.hammer_team = hammer_team      # team_id that has hammer this end
        self.powerplay_used = powerplay_used  # dict: {team1: bool, team2: bool}
        self.max_ends = max_ends
        self.prev_end_diff = prev_end_diff

        if powerplays_remaining is None:
            self.powerplays_remaining = {
                t: 1 for t in current_score.keys()
            }
        else:
            self.powerplays_remaining = powerplays_remaining

    def is_terminal(self):
        return self.end_number > self.max_ends 

    def legal_actions(self):
        if self.powerplays_remaining[self.hammer_team] > 0 and self.end_number > 2:
            return ["NO_PP", "PP"]
        return ["NO_PP"]

    def features_for_ev(self, team, action = None):
        opp = [t for t in self.current_score if t != team][0]
        if team == self.root_team:
            prev_end_diff_team = self.prev_end_diff
        else:
            prev_end_diff_team = -self.prev_end_diff
        return {
            "HasHammer": int(team == self.hammer_team),
            "PowerPlayBool": int(action == "PP") if action else 0,
            "EndID": self.end_number,
            "PrevScoreDiff": self.current_score[team] - self.current_score[opp],
            "PrevEndDiff": prev_end_diff_team
        }

    def sample_end_score(self, action):
        hammer = self.hammer_team
        no_hammer = [t for t in self.current_score if t != hammer][0]
        end = self.end_number
        dist = PROB_TABLE_END_DIFF[action][end]

        outcomes = list(dist.keys())
        probs = np.array(list(dist.values()), dtype=float)
        result = np.random.choice(outcomes, p=probs)

        if result > 0:
            return {hammer: result, no_hammer: 0}
        elif result < 0:
            return {hammer: 0, no_hammer: -result}
        else:
            return {hammer: 0, no_hammer: 0}

    def next_state(self, action):
        hammer = self.hammer_team
        no_hammer = [t for t in self.current_score if t != hammer][0]
        root = self.root_team
        opp = [t for t in self.current_score if t != root][0]

        score_delta = self.sample_end_score(action)

        new_score = self.current_score.copy()
        for t in new_score:
            new_score[t] += score_delta[t]

        end_diff = score_delta[root] - score_delta[opp]

        if score_delta[hammer] > 0:
            next_hammer = no_hammer
        elif score_delta[no_hammer] > 0:
            next_hammer = hammer
        else:
            next_hammer = no_hammer
        
        new_pp_used = self.powerplay_used.copy()
        new_pp_remaining = self.powerplays_remaining.copy()

        if action in ["PP"]:
            new_pp_used[hammer] = True
            new_pp_remaining[hammer] -= 1

        return GameState(
            current_score=new_score,
            end_number=self.end_number + 1,
            root_team=self.root_team,       
            hammer_team=next_hammer,       
            powerplay_used=new_pp_used,
            powerplays_remaining = new_pp_remaining,
            max_ends=self.max_ends,
            prev_end_diff=end_diff
        )
    
    
