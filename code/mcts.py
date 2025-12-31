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
        self._legal_actions = state.legal_actions()

    def is_fully_expanded(self):
        return len(self.children) == len(self._legal_actions)

    def best_child(self, c_param=1.4):
        best = None
        best_ucb = -float("inf")

        for child in self.children:
            if child.visits == 0:
                return child
            
            avg_reward = child.total_reward / child.visits
            ucb = avg_reward + c_param * math.sqrt(math.log(self.visits) / child.visits)

            if ucb > best_ucb:
                best_ucb = ucb
                best = child
    
        return best

    def expand(self, ev_model):
        tried_actions = [child.action_taken for child in self.children]
        untried_actions = [a for a in self._legal_actions if a not in tried_actions]
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
            opponent = [t for t in current_state.current_score if t != hammer][0]

            ev_scores = []
            for action in legal_actions:
                ev_hammer, _ = ev_model(current_state.features_for_ev(action, hammer, opponent, True))
                ev_opponent, _ = ev_model(current_state.features_for_ev(action, hammer, opponent, False))
                ev_net = ev_hammer - ev_opponent
                ev_scores.append(ev_net)
            
            e = np.exp(np.array(ev_scores))
            p = e / np.sum(e)
            action = np.random.choice(legal_actions, p=p)

            current_state = current_state.next_state(action, ev_model)

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
                child = node.expand(self.ev_model)
                if child:
                    node = child

            reward = node.simulate(self.ev_model)
            node.backpropagate(reward)

        if not root_node.children:
            return "NO_PP", 0
        
        for c in root_node.children:
            print(c.action_taken, "visits:", c.visits, "avg reward:", c.total_reward / (c.visits + 1e-6))

        best = max(root_node.children, key=lambda c: c.total_reward / (c.visits + 1e-6))
        
        return best.action_taken, best.total_reward / best.visits
        
       
