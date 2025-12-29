import torch
import pyro
import pyro.distributions as dist

# Load trained Bayesian model weights
posterior = torch.load("/Users/brentkong/Documents/curling/weights/unitddpm_<function BaysianRegression at 0x1208e0860>_weights.pt")

def bayesian_ev(features, posterior):
    f = torch.tensor([list(features.values())], dtype=torch.float)

    logits = f @ posterior["w"].T + posterior["b"]
    probs = dist.OrderedLogistic(logits, posterior["cutpoints"]).probs

    values = torch.arange(probs.shape[-1], dtype=torch.float)
    ev_per_sample = (probs * values).sum(-1)

    ev_mean = ev_per_sample.mean().item()
    ev_std = ev_per_sample.std().item()
    return ev_mean, ev_std

def bayesian_ev_continuous(features, posterior):
    f = torch.tensor([list(features.values())], dtype=torch.float)
    
    mu_samples = f @ posterior["w"].T + posterior["b"] 
    
    ev_mean = mu_samples.mean().item()
    ev_std = mu_samples.std().item()
    
    return ev_mean, ev_std


state = {
    "HasHammer": 1,
    "PowerPlay": 2,
    "PP_Right": 0.65,
    "PP_Left": 0.35,
    "BurialDepth": 100,
    "GuardAngle": 0.2,
    "ClusterIndex": 0.5,
    "SideOpenness": 4
}

ev_r = bayesian_ev_continuous(state, posterior)
ev_l = bayesian_ev_continuous(state, posterior)
print("EV Right:", ev_r, "EV Left:", ev_l)

# python baysian_ev.py