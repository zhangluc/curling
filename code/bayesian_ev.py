import torch
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEIGHTS_ROOT = PROJECT_ROOT / "weights" 

posterior_cont = torch.load(WEIGHTS_ROOT / "testing_weights" / "unitddpm_BaysianRegression_20260111_193054_82cf67d5_weights.pt")
production = torch.load(WEIGHTS_ROOT / "unitddpm_BaysianRegression_20260111_193019_830f987c_weights.pt")

def bayesian_eval_continuous(features, posterior = production):
    f = torch.tensor([list(features.values())], dtype=torch.float)
    
    mu_samples = f @ posterior["w"].T + posterior["b"] 
    
    ev_mean = mu_samples.mean().item()
    ev_std = mu_samples.std().item()
    
    return ev_mean, ev_std
