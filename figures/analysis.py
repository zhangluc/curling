import matplotlib.pyplot as plt
import json

with open('/Users/brentkong/Documents/curling/figures/simulations/frequency_dict_10000.json', 'r') as f:
    data = json.load(f)

frequency_dict = data[0]
wins_dict = data[1]
loss_dict = data[2]
draws_dict = data[3]

matches = frequency_dict.pop("matches")

frequency = True