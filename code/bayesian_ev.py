import torch
import pyro
import pyro.distributions as dist

posterior = torch.load("/Users/brentkong/Documents/curling/weights/unitddpm_<function BaysianRegression at 0x10f9e0ae0>_weights.pt")

def bayesian_eval_ordered(features, posterior = posterior):
    f = torch.tensor([list(features.values())], dtype=torch.float)

    logits = f @ posterior["w"].T + posterior["b"]
    probs = dist.OrderedLogistic(logits, posterior["cutpoints"]).probs

    values = torch.arange(probs.shape[-1], dtype=torch.float)
    ev_per_sample = (probs * values).sum(-1)

    ev_mean = ev_per_sample.mean().item()
    ev_std = ev_per_sample.std().item()
    return ev_mean, ev_std

def bayesian_eval_continuous(features, posterior = posterior):
    f = torch.tensor([list(features.values())], dtype=torch.float)
    
    mu_samples = f @ posterior["w"].T + posterior["b"] 
    
    ev_mean = mu_samples.mean().item()
    ev_std = mu_samples.std().item()
    
    return ev_mean, ev_std


if __name__ == "__main__":
    posterior = torch.load("/Users/brentkong/Documents/curling/weights/unitddpm_<function BaysianRegression at 0x10f9e0ae0>_weights.pt")

    features = {
        "Has_Hammer": 1,
        "PowerPlay": 1,
        "EndID": 7,
        "PrevScoreDiff": -2,
    }

    ev = bayesian_eval_continuous(features, posterior)
    print("EV:", ev)
