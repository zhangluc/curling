class GameState:
    def __init__(self, current_score, end_number, root_team, hammer_team, powerplay_used, max_ends=8, powerplays_remaining = 1):
        self.current_score = current_score  # dict: {team1: score1, team2: score2}
        self.end_number = end_number
        self.root_team = root_team
        self.hammer_team = hammer_team      # team_id that has hammer this end
        self.powerplay_used = powerplay_used  # dict: {team1: bool, team2: bool}
        self.max_ends = max_ends
        self.powerplays_remaining = powerplays_remaining

    def is_terminal(self):
        return self.end_number > self.max_ends 

    def legal_actions(self):
        if self.powerplays_remaining > 0 and not self.powerplay_used[self.hammer_team]:
            return ["NO_PP", "PP_RIGHT", "PP_LEFT"]
        return ["NO_PP"]

    def features_for_ev(self, action, hammer, non_hammer, is_hammer_team):
        return {
            "HasHammer": 1 if is_hammer_team else 0,
            "PP_NONE": 1 if action == "NO_PP" else 0, 
            "PP_LEFT": 1 if action == "PP_LEFT" else 0, 
            "PP_RIGHT": 1 if action == "PP_RIGHT" else 0, 
            "EndNumber": self.end_number,
            "PrevScoreDiff": 
            self.current_score[hammer] - self.current_score[non_hammer] 
            if is_hammer_team else 
            self.current_score[non_hammer] - self.current_score[hammer]
        }

    def next_state(self, action, ev_model):
        hammer = self.hammer_team
        non_hammer = [t for t in self.current_score.keys() if t != hammer][0]

        ev_hammer, _ = ev_model(self.features_for_ev(action, hammer, non_hammer, True))
        ev_non_hammer, _ = ev_model(self.features_for_ev(action, hammer, non_hammer, False))

        score_hammer = ev_hammer
        score_non_hammer = ev_non_hammer

        new_score = self.current_score.copy()
        new_score[hammer] += score_hammer
        new_score[non_hammer] += score_non_hammer

        # If hammer team scores, other team gets hammer.  
        # If team without hammer scores, hammer team keeps hammer.
        # If blank, switch hammer.
        if score_hammer > score_non_hammer:
            next_hammer = non_hammer  
        elif score_hammer < score_non_hammer:
            next_hammer = hammer       
        else: 
            next_hammer = non_hammer

        new_pp_used = self.powerplay_used.copy()
        new_pp_remaining = self.powerplays_remaining

        if action in ["PP_RIGHT", "PP_LEFT"]:
            new_pp_used[hammer] = True
            new_pp_remaining -= 1

        return GameState(
            current_score=new_score,
            end_number=self.end_number + 1,
            root_team=self.root_team,       
            hammer_team=next_hammer,       
            powerplay_used=new_pp_used,
            max_ends=self.max_ends,
            powerplays_remaining = new_pp_remaining
        )
    
    
