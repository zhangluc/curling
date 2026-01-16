import numpy as np
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data_processing" / "processed_data"
SAVE_DIR = PROJECT_ROOT / "figures" / "analysis" / "data_analysis"

stones = pd.read_csv(DATA_DIR / "stones_processed.csv")
ends   = pd.read_csv(DATA_DIR / "ends_with_counterfactual.csv")

task_labels = {
    "0":  "Draw",
    "1":  "Front",
    "2":  "Guard",
    "3":  "Raise/Tap-back",
    "4":  "Wick/Soft Peel",
    "5":  "Freeze",
    "6":  "Take-out",
    "7":  "Hit and Roll",
    "8":  "Clearing",
    "9":  "Double Take-out",
    "10": "Promotion Take-out",
    "11": "Through",
}

hammer_pp_status = (
    ends.loc[ends["Has_Hammer"] == 1, ["GameUID", "EndID", "Used_PP"]]
       .rename(columns={"Used_PP": "Opponent_PP"})
)

opening_shot_nonhammer = (
    stones.loc[stones["ShotID"] == 7]
        .merge(ends, on=["GameUID", "EndID", "TeamID"], how="inner")
        .rename(columns={"Has_Hammer_x": "Has_Hammer_Stone",
                         "Has_Hammer_y": "Has_Hammer_End"})
)

opening_shot_nonhammer = (
    opening_shot_nonhammer.loc[opening_shot_nonhammer["Has_Hammer_Stone"] == 0]
        .merge(hammer_pp_status, on=["GameUID", "EndID"], how="left")
)

opening_shot_summary = (
    opening_shot_nonhammer
        .groupby(["Task", "Opponent_PP"], dropna=False)
        .agg(
            Avg_Execution=("Points", lambda s: np.nanmean(s.to_numpy())),
            Avg_End_Points=("Result_y", lambda s: np.nanmean(s.to_numpy())),
            Big_End_Rate=("Result_y", lambda s: np.nanmean((s.to_numpy() >= 3).astype(float))),
            N=("Task", "size"),
        )
        .reset_index()
)

opening_shot_summary["Shot_Type"] = opening_shot_summary["Task"].astype(str).map(task_labels)
opening_shot_summary["Opponent_PP"] = np.where(
    opening_shot_summary["Opponent_PP"] == 1,
    "Opponent Used PP",
    "No Power Play",
)

opening_shot_summary["Shot_Type"] = np.where(
    opening_shot_summary["N"] < 20,
    "Other",
    opening_shot_summary["Shot_Type"],
)


def _wmean(values: pd.Series, weights: pd.Series) -> float:
    v = values.to_numpy(dtype=float)
    w = weights.to_numpy(dtype=float)
    mask = ~np.isnan(v) & ~np.isnan(w)
    if mask.sum() == 0:
        return np.nan
    return np.average(v[mask], weights=w[mask])

tmp = opening_shot_summary.copy()

tmp["w_exec"] = tmp["Avg_Execution"] * tmp["N"]
tmp["w_end"]  = tmp["Avg_End_Points"] * tmp["N"]
tmp["w_big"]  = tmp["Big_End_Rate"] * tmp["N"]

opening_shot_summary = (
    tmp.groupby(["Shot_Type", "Opponent_PP"], dropna=False, as_index=False)
       .agg(
           w_exec=("w_exec", "sum"),
           w_end=("w_end", "sum"),
           w_big=("w_big", "sum"),
           N=("N", "sum"),
       )
)

opening_shot_summary["Avg_Execution"]  = opening_shot_summary["w_exec"] / opening_shot_summary["N"]
opening_shot_summary["Avg_End_Points"] = opening_shot_summary["w_end"]  / opening_shot_summary["N"]
opening_shot_summary["Big_End_Rate"]   = opening_shot_summary["w_big"]  / opening_shot_summary["N"]

opening_shot_summary = (
    opening_shot_summary.drop(columns=["w_exec", "w_end", "w_big"])
        .sort_values(["Opponent_PP", "Avg_End_Points"], ascending=[True, False])
        .reset_index(drop=True)
)


print(opening_shot_summary)
print()
opening_shot_summary.to_csv(SAVE_DIR / "opening_shot.csv")

first_shot = (
    stones.loc[stones["ShotID"] == 7, ["GameUID", "EndID", "Task"]]
          .rename(columns={"Task": "First_Task"})
)

hammer_response = (
    stones.loc[stones["ShotID"] == 8]
        .merge(ends, on=["GameUID", "EndID", "TeamID"], how="inner")
        .rename(columns={"Has_Hammer_x": "Has_Hammer_Stone",
                         "Has_Hammer_y": "Has_Hammer_End"})
)

hammer_response = hammer_response.loc[hammer_response["Has_Hammer_Stone"] == 1]

response_analysis = (
    hammer_response
        .merge(first_shot, on=["GameUID", "EndID"], how="inner")
        .groupby(["First_Task", "Task", "Used_PP"], dropna=False)
        .agg(
            Avg_Execution=("Points", lambda s: np.nanmean(s.to_numpy())),
            Avg_End_Points=("Result_y", lambda s: np.nanmean(s.to_numpy())),
            Big_End_Rate=("Result_y", lambda s: np.nanmean((s.to_numpy() >= 3).astype(float))),
            N=("Task", "size"),
        )
        .reset_index()
)

response_analysis = response_analysis.loc[response_analysis["N"] >= 15].copy()

response_analysis["First_Shot"] = response_analysis["First_Task"].astype(str).map(task_labels)
response_analysis["Hammer_Shot"] = response_analysis["Task"].astype(str).map(task_labels)

response_analysis = (
    response_analysis
        .sort_values("Avg_End_Points", ascending=False)
        .reset_index(drop=True)
)


plot_data = response_analysis.copy()
plot_data["Used_PP"] = pd.Categorical(
    plot_data["Used_PP"],
    categories=[0, 1],
    ordered=False
)
plot_data["Used_PP"] = plot_data["Used_PP"].cat.rename_categories(["No Power Play", "Power Play"])

plot_data["First_Shot"] = pd.Categorical(plot_data["First_Shot"])
plot_data["Hammer_Shot"] = pd.Categorical(plot_data["Hammer_Shot"])
plot_data = plot_data[["First_Shot", "Hammer_Shot", "Used_PP", "Avg_Execution", "Avg_End_Points", "Big_End_Rate", "N"]]

print(plot_data)
plot_data.to_csv(SAVE_DIR / "hammer_response.csv")
