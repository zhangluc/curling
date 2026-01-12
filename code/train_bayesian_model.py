import pandas as pd
import torch
import pyro
import pyro.distributions as dist
from pyro.infer import MCMC, NUTS

df = pd.read_csv("/Users/brentkong/Documents/curling/data_processing/train_test_data/train_df.csv")

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

    torch.save(posterior, f"/Users/brentkong/Documents/curling/weights/testing_weights/unitddpm_{model}_weights.pt")
