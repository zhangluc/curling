import torch
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEIGHTS_ROOT = PROJECT_ROOT / "weights" 

posterior_cont = torch.load(WEIGHTS_ROOT / "testing_weights" / "unitddpm_<function BaysianRegression at 0x122cf0cc0>_weights.pt")
production = torch.load(WEIGHTS_ROOT / "unitddpm_<function BaysianRegression at 0x1196f0cc0>_weights.pt")

def bayesian_eval_continuous(features, posterior = production):
    f = torch.tensor([list(features.values())], dtype=torch.float)
    
    mu_samples = f @ posterior["w"].T + posterior["b"] 
    
    ev_mean = mu_samples.mean().item()
    ev_std = mu_samples.std().item()
    
    return ev_mean, ev_std
