import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
    "axes.titleweight": "semibold",
    "font.size": 14,
})

def apply_standard_axes(ax, *, grid=True):
    """Consistent cosmetics for every axis."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(grid)
    if grid:
        ax.grid(alpha=plt.rcParams["grid.alpha"], linestyle=plt.rcParams["grid.linestyle"])

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data_processing" / "processed_data"
SAVE_DIR = PROJECT_ROOT / "figures" / "graphs"

ends   = pd.read_csv(DATA_DIR / "ends_processed.csv")
games  = pd.read_csv(DATA_DIR / "games_processed.csv")
stones = pd.read_csv(DATA_DIR / "stones_processed.csv")
ends_counterfactual = pd.read_csv(DATA_DIR / "ends_with_counterfactual.csv")

if "Used_PP" not in ends.columns and "PowerPlayBool" in ends.columns:
    ends = ends.rename(columns={"PowerPlayBool": "Used_PP"})

required = ["Used_PP", "Has_Hammer", "Result", "EndID", "GameUID", "TeamID"]
missing = [c for c in required if c not in ends.columns]
if missing:
    raise KeyError(f"Missing columns in ends: {missing}\nAvailable: {list(ends.columns)}")






tmp = ends_counterfactual.loc[
    (ends_counterfactual["Used_PP"] == 1) & (ends_counterfactual["Has_Hammer"] == 1),
    ["GameUID", "Result", "Result_No_PP"],
].copy()
tmp["delta"] = tmp["Result"] - tmp["Result_No_PP"]
game_level_effect = tmp.groupby("GameUID", as_index=False).agg(PP_Gain=("delta", "sum"))

x = game_level_effect["PP_Gain"].dropna().to_numpy()
mean_x = x.mean()

bw = 0.5
offset = 0.25  
start = np.floor((x.min() - offset) / bw) * bw + offset
end   = np.ceil((x.max() - offset) / bw) * bw + offset
bins = np.arange(start, end + bw, bw)

fig, ax = plt.subplots(figsize=(9, 6))
ax.hist(x, bins=bins, color="steelblue", edgecolor="white", linewidth=1.0)

ax.axvline(0, linestyle="--", color="red", linewidth=2)
ax.axvline(mean_x, color="darkblue", linewidth=2)

ax.set_xlim(-6, 6)

ax.set_xlabel("Points gained from Power Play (Actual – No PP)")
ax.set_ylabel("Number of games")
apply_standard_axes(ax, grid=True)

plt.tight_layout()
plt.savefig(SAVE_DIR / "distribution_pp_tail.png", bbox_inches="tight")
plt.show()






ends_with_context = ends_counterfactual.sort_values(["GameUID", "EndID"]).copy()

ends_with_context["Opponent_Result"] = (
    ends_with_context.groupby(["GameUID", "EndID"])["Result"]
    .transform(lambda s: s.iloc[::-1].to_numpy())
)

ends_with_context = ends_with_context.sort_values(["GameUID", "TeamID", "EndID"])
ends_with_context["Cumulative_Score"] = ends_with_context.groupby(["GameUID", "TeamID"])["Result"].cumsum()
ends_with_context["Opponent_Cumulative"] = ends_with_context.groupby(["GameUID", "TeamID"])["Opponent_Result"].cumsum()

ends_with_context["Score_Diff_Before"] = (
    ends_with_context.groupby(["GameUID", "TeamID"])["Cumulative_Score"].shift(1).fillna(0)
    - ends_with_context.groupby(["GameUID", "TeamID"])["Opponent_Cumulative"].shift(1).fillna(0)
)






pp_success_context = ends_with_context.loc[
    (ends_with_context["Used_PP"] == 1) & (ends_with_context["Has_Hammer"] == 1)
].copy()

pp_success_context["Game_Context"] = np.select(
    [
        pp_success_context["Score_Diff_Before"] < -3,
        pp_success_context["Score_Diff_Before"] < 0,
        pp_success_context["Score_Diff_Before"] == 0,
        pp_success_context["Score_Diff_Before"] <= 3,
    ],
    ["Behind >3", "Behind 1–3", "Tied", "Ahead 1–3"],
    default="Ahead >3",
)

pp_success_context["PP_Gain"] = pp_success_context["Result"] - pp_success_context["Result_No_PP"]

pp_context_summary = (
    pp_success_context.groupby(["EndID", "Game_Context"], as_index=False)
    .agg(Avg_PP_Gain=("PP_Gain", "mean"), N=("PP_Gain", "size"))
)
pp_context_summary = pp_context_summary.loc[pp_context_summary["N"] >= 5].copy()

pivot_vals = pp_context_summary.pivot(index="Game_Context", columns="EndID", values="Avg_PP_Gain")
pivot_n    = pp_context_summary.pivot(index="Game_Context", columns="EndID", values="N")

context_order = ["Behind >3", "Behind 1–3", "Tied", "Ahead 1–3", "Ahead >3"]
pivot_vals = pivot_vals.reindex(context_order)
pivot_n = pivot_n.reindex(context_order)

annot = pivot_vals.copy().astype(object)
for r in annot.index:
    for c in annot.columns:
        v = pivot_vals.loc[r, c]
        n = pivot_n.loc[r, c]
        annot.loc[r, c] = "" if (pd.isna(v) or pd.isna(n)) else f"{v:.2f}\n(n={int(n)})"

fig, ax = plt.subplots(figsize=(9, 6))

sns.heatmap(
    pivot_vals,
    ax=ax,
    annot=annot,
    fmt="",
    center=0,
    vmin=-2,
    vmax=2,
    cmap=sns.diverging_palette(10, 130, as_cmap=True),
    linewidths=0.5,
    linecolor="white",
    cbar_kws={"label": "PP Gain"},
)

ax.set_xlabel("End Number")
ax.set_ylabel("Score Situation")

apply_standard_axes(ax, grid=False)

plt.tight_layout()
plt.savefig(SAVE_DIR / "pp_effectiveness.png", bbox_inches="tight")
plt.show()


