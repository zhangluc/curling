import math
import random
import numpy as np
from copy import deepcopy

class MCTSNode:
    def __init__(self, state, parent=None, action_taken=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.total_reward = 0.0
        self.action_taken = action_taken  

    def is_fully_expanded(self):
        return len(self.children) == len(self.state.legal_actions())

    def best_child(self, c_param=1.4):
        choices_weights = [
            (child.total_reward / child.visits) + 
            c_param * math.sqrt((2 * math.log(self.visits) / child.visits))
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]

    def expand(self, ev_model):
        tried_actions = [child.action_taken for child in self.children]
        untried_actions = [a for a in self.state.legal_actions() if a not in tried_actions]
        if not untried_actions:
            return None

        action = random.choice(untried_actions)
        next_state = self.state.next_state(action, ev_model)
        child_node = MCTSNode(next_state, parent=self, action_taken=action)
        self.children.append(child_node)
        return child_node

    def simulate(self, ev_model):
        current_state = deepcopy(self.state)
        root_team = self.state.root_team

        while not current_state.is_terminal():
            legal_actions = current_state.legal_actions()
            hammer = current_state.hammer_team
            non_hammer = [t for t in current_state.current_score.keys() if t != hammer][0]

            ev_scores = []
            for action in legal_actions:
                ev_hammer, _ = ev_model(current_state.features_for_ev(action, hammer, non_hammer, True))
                ev_non_hammer, _ = ev_model(current_state.features_for_ev(action, hammer, non_hammer, False))
                ev_net = ev_hammer - ev_non_hammer

                if hammer != root_team:
                    ev_net *= -1

                ev_scores.append(ev_net)
            
            best_idx = ev_scores.index(max(ev_scores))
            action = legal_actions[best_idx]

            current_state = current_state.next_state(action, ev_model)

        #reward = current_state.current_score[root_team] - current_state.current_score[
        #    [t for t in current_state.current_score if t != root_team][0]
        #]
        reward = current_state.current_score[root_team]
        return reward
    
    def backpropagate(self, reward):
        self.visits += 1
        self.total_reward += reward
        if self.parent:
            self.parent.backpropagate(reward)


class MCTS:
    def __init__(self, ev_model, num_simulations):
        self.ev_model = ev_model
        self.num_simulations = num_simulations

    def search(self, root_state):
        root_node = MCTSNode(root_state)
        for _ in range(self.num_simulations):
            node = root_node
            while node.is_fully_expanded() and node.children:
                node = node.best_child()
            if not node.state.is_terminal():
                node = node.expand(self.ev_model)
            reward = node.simulate(self.ev_model)
            node.backpropagate(reward)

        best_child = max(root_node.children, key=lambda c: c.total_reward / c.visits)
        best_action = best_child.action_taken

        rewards = []
        for child in root_node.children:
            avg = child.total_reward / child.visits if child.visits > 0 else 0
            rewards.append(avg)

        expected_score = np.mean(rewards)
        uncertainty = np.std(rewards)

        return best_action, expected_score, uncertainty
