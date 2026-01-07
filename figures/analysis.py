import pandas as pd
import numpy as np
import json


with open('/Users/brentkong/Documents/curling/figures/simulations/frequency_dict_100000_new.json', 'r') as f:
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
"PP_called_End6_margin_after6": weighted_stats(by_margin_raw_7)}

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

df.to_csv(f'/Users/brentkong/Documents/curling/figures/analysis/simulation_statistics/analysis_{matches}.csv', index = False)
df2.to_csv(f'/Users/brentkong/Documents/curling/figures/analysis/simulation_statistics/analysis_margin{matches}.csv', index = False)