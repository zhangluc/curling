import pandas as pd
import json


with open('/Users/brentkong/Documents/curling/figures/simulations/frequency_dict_100000.json', 'r') as f:
    data = json.load(f)

frequency_dict = data[0]
wins_dict = data[1]
loss_dict = data[2]
draws_dict = data[3]
matches = frequency_dict.pop("matches")
pp_matches = sum(frequency_dict.values())

hammer_start = data[4]["hammer_start"]
hammer_no_start = data[4]["no_hammer_start"]
hammer_start_matches = hammer_start.pop("matches")
hammer_no_start_matches = hammer_no_start.pop("matches")

frequency_percent_dict, win_percent_dict, draw_percent_dict, loss_percent_dict, win_draw_dict = ({} for _ in range(5))
for key, value in frequency_dict.items():
    frequency_percent_dict[key] = frequency_dict[key] / pp_matches
    win_percent_dict[key] = (wins_dict[key]) / (frequency_dict[key] if frequency_dict[key] != 0 else 1)
    draw_percent_dict[key] = (draws_dict[key]) / (frequency_dict[key] if frequency_dict[key] != 0 else 1)
    loss_percent_dict[key] = (loss_dict[key]) / (frequency_dict[key] if frequency_dict[key] != 0 else 1)
    win_draw_dict[key] = (wins_dict[key] + draws_dict[key]) / (frequency_dict[key] if frequency_dict[key] != 0 else 1)


df = pd.DataFrame({
    'End': [int(k) for k in frequency_dict.keys()],
    'Frequency %': list(frequency_percent_dict.values()),
    'Win %': list(win_percent_dict.values()),
    'Draw %': list(draw_percent_dict.values()),
    'Loss %': list(loss_percent_dict.values()),
    'Win + Draw %': list(win_draw_dict.values())
})

df.index = df.index.astype(int)

df.to_csv(f'/Users/brentkong/Documents/curling/figures/analysis/analysis_{matches}.csv', index = False)