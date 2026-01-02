from bayesian_ev import bayesian_eval_continuous, bayesian_eval_ordered
import pandas as pd
import torch

def neg_log_likelihood(pred_means, pred_stds, y):
    pred_stds = torch.clamp(pred_stds, min=1e-6)
    dist = torch.distributions.Normal(pred_means, pred_stds)
    return -dist.log_prob(y).mean()

def coverage(y, mu, sigma):
    z = torch.tensor(1.96)
    lower = mu - z * sigma
    upper = mu + z * sigma
    return ((y >= lower) & (y <= upper)).float().mean()

def test_model(X, y, model):
    mus, sigmas, ys = [], [], []

    for i in range(len(X)):
        x_row = X.iloc[i].to_dict()
        mu, sigma = model(x_row)

        mus.append(mu)
        sigmas.append(sigma)
        ys.append(y.iloc[i])

    mus = torch.tensor(mus)
    sigmas = torch.tensor(sigmas)
    ys = torch.tensor(ys)

    return {
        "RMSE": torch.sqrt(((mus - ys) ** 2).mean()).item(),
        "NLL": neg_log_likelihood(mus, sigmas, ys).item(),
        "Coverage95": coverage(ys, mus, sigmas).item(),
        "Sharpness": sigmas.mean().item(),
    }


if __name__ == "__main__":
    features = ["Has_Hammer", "PowerPlayBool", "EndID", "PrevScoreDiff"]

    test_df = pd.read_csv(
        "/Users/brentkong/Documents/curling/data_processing/train_test_data/test_df.csv"
    )

    X = test_df[features]
    y = test_df["Result"]

    results_cont = test_model(X, y, bayesian_eval_continuous)
    results_ord = test_model(X, y, bayesian_eval_ordered)


    pd.DataFrame([results_cont]).to_csv(
        "/Users/brentkong/Documents/curling/data_processing/Model_Results_Continuous.csv",
        index=False
    )

    pd.DataFrame([results_ord]).to_csv(
        "/Users/brentkong/Documents/curling/data_processing/Model_Results_Ordered.csv",
        index=False
    )