import torch
import pyro
import pyro.distributions as dist

posterior_ord = torch.load("/Users/brentkong/Documents/curling/weights/testing_weights/unitddpm_<function OrderedLogistic at 0x120cf09a0>_weights.pt")
posterior_cont = torch.load("/Users/brentkong/Documents/curling/weights/testing_weights/unitddpm_<function BaysianRegression at 0x10fef0cc0>_weights.pt")
posterior = torch.load("/Users/brentkong/Documents/curling/weights/unitddpm_<function BaysianRegression at 0x12d9e0ae0>_weights.pt")

def bayesian_eval_ordered(features, posterior = posterior_ord):
    f = torch.tensor([list(features.values())], dtype=torch.float)

    logits = f @ posterior["w"].T + posterior["b"]
    cutpoints = torch.cumsum(torch.nn.functional.softplus(posterior["raw_cutpoints"]), dim=-1)
    probs = dist.OrderedLogistic(logits, cutpoints).probs

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
