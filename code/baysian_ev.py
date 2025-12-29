import torch

def bayesian_ev(features, side):
    """Estimate EV of calling Power Play on a side using posterior samples"""
    f = torch.tensor([features], dtype=torch.float)
    w_samples = posterior["w"]
    b_samples = posterior["b"]

    # Compute EV over posterior
    evs = torch.exp(f @ w_samples.T + b_samples)
    return evs.mean().item()

state = {
    "PowerPlay": 0,  # not used yet
    "HasHammer": 1,
    "ScoreDiff": -1,
    "PP_Right": 0.65,
    "PP_Left": 0.35,
    "BurialDepth": 100,
    "GuardAngle": 0.2,
    "ClusterIndex": 0.5,
    "SideOpenness": 4
}

ev_r = bayesian_ev(state, 1)
ev_l = bayesian_ev(state, 2)
print("EV Right:", ev_r, "EV Left:", ev_l)