import pyro
import uuid
import torch
import pandas as pd
from pathlib import Path
from datetime import datetime
import pyro.distributions as dist
from pyro.infer import MCMC, NUTS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data_processing" / "train_test_data"
SAVE_DIR = PROJECT_ROOT / "weights" / "testing_weights"

df = pd.read_csv(DATA_DIR / "train_df.csv")

features = ["Has_Hammer",
            "PowerPlayBool",
            "EndID",
            "PrevScoreDiff",
            "PrevEndDiff"]

X = torch.tensor(df[features].values, dtype=torch.float)
y = torch.tensor(df["Result"].values, dtype=torch.long)

def BaysianRegression(X, y=None):
    _, d = X.shape
    w = pyro.sample("w", dist.Normal(0, 1).expand([d]).to_event(1))
    b = pyro.sample("b", dist.Normal(0, 1))
    sigma = pyro.sample("sigma", dist.HalfCauchy(1.0))
    mu = X @ w + b
    pyro.sample("obs", dist.Normal(mu, sigma), obs=y)

if __name__ == "__main__":
    model = BaysianRegression
    nuts_kernel = NUTS(model)
    mcmc = MCMC(nuts_kernel, num_samples=1000, warmup_steps=200)
    mcmc.run(X, y)

    posterior = mcmc.get_samples()
    print(posterior["w"].mean(0), posterior["b"].mean())
    print("Posterior b:", posterior["b"].mean())

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    uid = uuid.uuid4().hex[:8]
    model_name = model.__name__

    filename = f"unitddpm_{model_name}_{timestamp}_{uid}_weights.pt"

    torch.save(posterior, SAVE_DIR / filename)

    print(f"Saved weights to: {SAVE_DIR / filename}")