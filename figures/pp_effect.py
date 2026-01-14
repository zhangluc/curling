import numpy as np
import pandas as pd
import seaborn as sns
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

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
    """
    Apply consistent cosmetics to a Matplotlib Axes.
    For heatmaps, pass grid=False to avoid overlaying dashed grid lines on tiles.
    """
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(grid)
    if grid:
        ax.grid(alpha=plt.rcParams["grid.alpha"], linestyle=plt.rcParams["grid.linestyle"])

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data_processing" / "processed_data"
SAVE_DIR = PROJECT_ROOT / "figures" / "graphs"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

stones = pd.read_csv(DATA_DIR / "stones_processed.csv")
ends   = pd.read_csv(DATA_DIR / "ends_with_counterfactual.csv")  

task_labels = {
    0: "Draw",
    1: "Front",
    2: "Guard",
    3: "Raise/Tap-back",
    4: "Wick/Soft Peel",
    5: "Freeze",
    6: "Take-out",
    7: "Hit and Roll",
    8: "Clearing",
    9: "Double Take-out",
    10: "Promotion Take-out",
    11: "Through",
}

first_shot = (
    stones.loc[stones["ShotID"] == 7, ["GameUID", "EndID", "Task"]]
    .rename(columns={"Task": "First_Task"})
)

hammer_response = (
    stones.loc[stones["ShotID"] == 8]
    .merge(ends, on=["GameUID", "EndID", "TeamID"], how="inner", suffixes=("_stone", "_end"))
)

hammer_response = hammer_response.loc[hammer_response["Has_Hammer_stone"] == 1].copy()

pp_col = "Used_PP" if "Used_PP" in hammer_response.columns else (
    "PowerPlayBool" if "PowerPlayBool" in hammer_response.columns else None
)
if pp_col is None:
    raise KeyError("Couldn't find PP flag. Expected 'Used_PP' or 'PowerPlayBool'.")

result_col = "Result_end" if "Result_end" in hammer_response.columns else (
    "Result" if "Result" in hammer_response.columns else None
)
if result_col is None:
    raise KeyError("Couldn't find end result column. Expected 'Result_end' or 'Result'.")

response_analysis = (
    hammer_response
    .merge(first_shot, on=["GameUID", "EndID"], how="inner")
    .groupby(["First_Task", "Task", pp_col], as_index=False)
    .agg(
        Avg_End_Points=(result_col, "mean"),
        N=("Task", "size"),
    )
)

response_analysis = response_analysis.loc[response_analysis["N"] >= 15].copy()

response_analysis["First_Shot"] = response_analysis["First_Task"].map(task_labels)
response_analysis["Hammer_Shot"] = response_analysis["Task"].map(task_labels)
response_analysis["Used_PP_Label"] = np.where(
    response_analysis[pp_col].astype(int) == 1, "Power Play", "No Power Play"
)

response_analysis = response_analysis.dropna(subset=["First_Shot", "Hammer_Shot"])

midpoint_score = response_analysis["Avg_End_Points"].mean()
shot_order = [task_labels[k] for k in sorted(task_labels.keys())]

sns.set_theme(style="white")

def draw_heatmap(ax, df, title):
    pivot = (
        df.pivot(index="Hammer_Shot", columns="First_Shot", values="Avg_End_Points")
          .reindex(index=shot_order, columns=shot_order)
    )
    annot = pivot.round(2).astype(object).where(~pivot.isna(), "")

    hm = sns.heatmap(
        pivot,
        ax=ax,
        annot=annot,
        fmt="",
        square=True,
        linewidths=0.6,
        linecolor="0.85",
        cmap=sns.diverging_palette(10, 130, as_cmap=True),
        center=midpoint_score,
        cbar=False
    )

    apply_standard_axes(ax, grid=False)

    ax.set_title(title)
    ax.set_xlabel("Opponent Opening Shot (ShotID = 7)")
    ax.set_ylabel("Hammer Response (ShotID = 8)")

    ax.set_xticklabels(shot_order, rotation=40, ha="right", rotation_mode="anchor")
    ax.set_yticklabels(shot_order, rotation=0)

    ax.tick_params(axis="x", labelsize=11, pad=8)
    ax.tick_params(axis="y", labelsize=11)
    return hm

fig = plt.figure(figsize=(22, 9))

gs = gridspec.GridSpec(
    1, 3,
    width_ratios=[1, 1, 0.04],
    wspace=0.25
)

ax0 = fig.add_subplot(gs[0, 0])
ax1 = fig.add_subplot(gs[0, 1])
cax = fig.add_subplot(gs[0, 2])  

df_no  = response_analysis.loc[response_analysis["Used_PP_Label"] == "No Power Play"]
df_yes = response_analysis.loc[response_analysis["Used_PP_Label"] == "Power Play"]

hm0 = draw_heatmap(ax0, df_no,  "No Power Play")
hm1 = draw_heatmap(ax1, df_yes, "Power Play")

mappable = ax1.collections[0]
cbar = fig.colorbar(mappable, cax=cax)
cbar.set_label("Avg End Points")

fig.suptitle(
    "Hammer Team Response to Opening Shot\nAverage end points scored by hammer team",
    fontsize=18,
    x=0.06, ha="left", y=0.98
)

fig.subplots_adjust(top=0.85, bottom=0.18)


plt.savefig(SAVE_DIR / "pp_effective_heatmap.png")
plt.show()
