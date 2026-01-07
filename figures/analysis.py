import pandas as pd
import numpy as np
import json

df = pd.read_csv("/Users/brentkong/Documents/curling/data_processing/processed_data/ends_processed.csv")

def stats_from_series(s: pd.Series):
    """Return mean/median/mode/quantiles in the same schema you used."""
    s = pd.to_numeric(s, errors="coerce").dropna()
    if len(s) == 0:
        return {"Mean": np.nan, "Median": np.nan, "Mode": np.nan,
                "Q25": np.nan, "Q75": np.nan, "IQR": np.nan, "P10": np.nan, "P90": np.nan}

    vals, counts = np.unique(s.values, return_counts=True)
    mode = vals[np.argmax(counts)]

    q25 = np.percentile(s, 25)
    q75 = np.percentile(s, 75)
    p10 = np.percentile(s, 10)
    p90 = np.percentile(s, 90)

    return {
        "Mean": float(np.mean(s)),
        "Median": float(np.median(s)),
        "Mode": float(mode),
        "Q25": float(q25),
        "Q75": float(q75),
        "IQR": float(q75 - q25),
        "P10": float(p10),
        "P90": float(p90)
    }

pp = df[df["PowerPlayBool"] == 1].copy()

pp_counts = pp.groupby("EndID").size().sort_index()
pp_total = int(pp_counts.sum())
pp_freq_pct = (pp_counts / pp_total).sort_index()

finals = (
    df.sort_values("EndID")
      .groupby(["GameUID", "TeamID"], as_index=False)
      .tail(1)
      .copy()
)

finals["Win"]  = finals["CumulativeScore"] > finals["OpponentCumulative"]
finals["Draw"] = finals["CumulativeScore"] == finals["OpponentCumulative"]
finals["Loss"] = finals["CumulativeScore"] < finals["OpponentCumulative"]

pp = pp.merge(
    finals[["GameUID", "TeamID", "Win", "Draw", "Loss"]],
    on=["GameUID", "TeamID"],
    how="left"
)

pp_win = pp.groupby("EndID")["Win"].mean().sort_index()
pp_draw = pp.groupby("EndID")["Draw"].mean().sort_index()
pp_loss = pp.groupby("EndID")["Loss"].mean().sort_index()
pp_win_draw = (pp_win + pp_draw).sort_index()

pp_6_8 = pp[pp["EndID"].isin([6, 7, 8])].copy()

pp_6_8_hammer = pp_6_8[pp_6_8["Has_Hammer"] == 1]
use_for_margin = pp_6_8_hammer if len(pp_6_8_hammer) > 0 else pp_6_8

margin_stats = {}
for end in [6, 7, 8]:
    subset = use_for_margin[use_for_margin["EndID"] == end]["PrevScoreDiff"]
    margin_stats[f"PP_called_End{end}_entry_margin"] = stats_from_series(subset)

summary_df = pd.DataFrame({
    "End": pp_counts.index.astype(int),
    "PP Calls": pp_counts.values.astype(int),
    "Frequency %": pp_freq_pct.values,
    "Win %": pp_win.reindex(pp_counts.index).values,
    "Draw %": pp_draw.reindex(pp_counts.index).values,
    "Loss %": pp_loss.reindex(pp_counts.index).values,
    "Win + Draw %": pp_win_draw.reindex(pp_counts.index).values
}).sort_values("End")

margin_df = pd.DataFrame.from_dict(margin_stats, orient="index")
margin_df.index.name = "Dataset"
margin_df.reset_index(inplace=True)

summary_df.to_csv("/Users/brentkong/Documents/curling/figures/analysis/simulation_statistics/powerplay_end_summary.csv", index=False)
margin_df.to_csv("/Users/brentkong/Documents/curling/figures/analysis/simulation_statistics/powerplay_entry_margin_stats_6_8.csv", index=False)


with open('/Users/brentkong/Documents/curling/figures/simulations/frequency_dict_10000.json', 'r') as f:
    data = json.load(f)

def weighted_stats(by_margin):
    margins = []
    for k, v in by_margin.items():
        margins.extend([int(k)] * v)

    margins = np.array(margins)

    mean = margins.mean()
    median = np.median(margins)
    values, counts = np.unique(margins, return_counts=True)
    mode = values[np.argmax(counts)]

    q25 = np.percentile(margins, 25)
    q75 = np.percentile(margins, 75)
    p10 = np.percentile(margins, 10)
    p90 = np.percentile(margins, 90)

    return {
        "Mean": mean,
        "Median": median,
        "Mode": mode,
        "Q25": q25,
        "Q75": q75,
        "IQR": q75 - q25,
        "P10": p10,
        "P90": p90
    }



frequency_dict = data[0]
wins_dict = data[1]
loss_dict = data[2]
draws_dict = data[3]
by_margin_raw_6 = data[6]["by_margin"]
by_margin_raw_7 = data[8]["by_margin"]
by_margin_raw_8 = data[10]["by_margin"]
matches = frequency_dict.pop("matches")
pp_matches = sum(frequency_dict.values())

frequency_percent_dict, win_percent_dict, draw_percent_dict, loss_percent_dict, win_draw_dict = ({} for _ in range(5))
for key, value in frequency_dict.items():
    frequency_percent_dict[key] = frequency_dict[key] / pp_matches
    win_percent_dict[key] = (wins_dict[key]) / (frequency_dict[key] if frequency_dict[key] != 0 else 1)
    draw_percent_dict[key] = (draws_dict[key]) / (frequency_dict[key] if frequency_dict[key] != 0 else 1)
    loss_percent_dict[key] = (loss_dict[key]) / (frequency_dict[key] if frequency_dict[key] != 0 else 1)
    win_draw_dict[key] = (wins_dict[key] + draws_dict[key]) / (frequency_dict[key] if frequency_dict[key] != 0 else 1)


value_dict = {"PP_called_End6_margin_after5": weighted_stats(by_margin_raw_6),
"PP_called_End6_margin_after6": weighted_stats(by_margin_raw_7),
"PP_called_End7_margin_after6": weighted_stats(by_margin_raw_8),
}

df = pd.DataFrame({
    'End': [int(k) for k in frequency_dict.keys()],
    'Frequency %': list(frequency_percent_dict.values()),
    'Win %': list(win_percent_dict.values()),
    'Draw %': list(draw_percent_dict.values()),
    'Loss %': list(loss_percent_dict.values()),
    'Win + Draw %': list(win_draw_dict.values())
})

df2 = pd.DataFrame.from_dict(value_dict, orient="index")
df2.index.name = "Dataset"
df2.reset_index(inplace=True)


df.index = df.index.astype(int)

df.to_csv(f'/Users/brentkong/Documents/curling/figures/analysis/simulation_statistics/analysis_{matches}_both.csv', index = False)
df2.to_csv(f'/Users/brentkong/Documents/curling/figures/analysis/simulation_statistics/analysis_margin{matches}_both.csv', index = False)