import torch
import pyro
import pyro.distributions as dist

posterior_cont = torch.load("/Users/brentkong/Documents/curling/weights/testing_weights/unitddpm_<function BaysianRegression at 0x122cf0cc0>_weights.pt")
production = torch.load("/Users/brentkong/Documents/curling/weights/unitddpm_<function BaysianRegression at 0x1196f0cc0>_weights.pt")

def bayesian_eval_continuous(features, posterior = posterior_cont):
    f = torch.tensor([list(features.values())], dtype=torch.float)
    
    mu_samples = f @ posterior["w"].T + posterior["b"] 
    
    ev_mean = mu_samples.mean().item()
    ev_std = mu_samples.std().item()
    
    return ev_mean, ev_std
