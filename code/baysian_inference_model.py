import pandas as pd
import torch
import pyro
import pyro.distributions as dist
from pyro.infer import MCMC, NUTS

df = pd.read_csv("/Users/brentkong/Documents/curling/processed_data/ends_processed.csv")

features = ["PowerPlay", "HasHammer", "ScoreDiff", "PP_Right", "PP_Left",
            "BurialDepth", "GuardAngle", "ClusterIndex", "SideOpenness"]

X = torch.tensor(df[features].values, dtype=torch.float)
y = torch.tensor(df["Result"].values, dtype=torch.long)

def model(X, y=None):
    n, d = X.shape

    # Priors for weights + bias
    w = pyro.sample("w", dist.Normal(0, 1).expand([d]).to_event(1))
    b = pyro.sample("b", dist.Normal(0, 1))

    # Ordinal cutpoints (monotonic constraint)
    c1 = pyro.sample("c1", dist.Normal(1, 1))
    c2 = pyro.sample("c2", dist.Normal(2, 1))
    c3 = pyro.sample("c3", dist.Normal(3, 1))
    c4 = pyro.sample("c4", dist.Normal(4, 1))
    c5 = pyro.sample("c5", dist.Normal(5, 1))

    cutpoints = torch.stack([c1, c2, c3, c4, c5])

    # Linear score
    logits = X @ w + b

    # Likelihood
    obs = pyro.sample("obs", dist.OrderedLogistic(logits, cutpoints), obs=y)
    return obs

# Run inference
nuts_kernel = NUTS(model)
mcmc = MCMC(nuts_kernel, num_samples=1000, warmup_steps=200)
mcmc.run(X, y)

posterior = mcmc.get_samples()
print(posterior["w"].mean(0), posterior["b"].mean())

