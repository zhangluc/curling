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
    mus, ys = [], []

    for i in range(len(X)):
        x_row = X.iloc[i].to_dict()
        mu, _ = model(x_row)

        mus.append(mu)
        ys.append(y.iloc[i])

    mus = torch.tensor(mus, dtype = torch.float) 
    ys = torch.tensor(ys, dtype = torch.float)

    rmse = torch.sqrt(((mus - ys) ** 2).mean()).item()
    mae = torch.mean(torch.abs(mus - ys)).item()
    bias = torch.mean(mus - ys).item()
    r2 = 1 - torch.sum((mus - ys) ** 2) / torch.sum((ys - ys.mean()) ** 2)
    r2 = r2.item()

    return {
        "RMSE": rmse,
        "MAE": mae,
        "Bias": bias,
        "R2": r2
    }


if __name__ == "__main__":
    features = ["Has_Hammer", "PowerPlayBool", "EndID", "PrevScoreDiff", "PrevEndDiff"]

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