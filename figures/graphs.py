import matplotlib.pyplot as plt
import json

with open('/Users/brentkong/Documents/curling/figures/simulations/frequency_dict_10000.json', 'r') as f:
    data = json.load(f)

frequency_dict = data[0]
wins_dict = data[1]
loss_dict = data[2]
draws_dict = data[3]
matches = frequency_dict.pop("matches")

hammer_start = data[4][0]
hammer_no_start = data[4][1]
hammer_start_matches = data[4][0].pop("matches")
hammer_no_start_matches = data[4][1].pop("matches")

frequency = True

if frequency: 
    categories = list(frequency_dict.keys())
    frequencies = list(frequency_dict.values())

    plt.figure(figsize=(8, 6))
    plt.bar(categories, frequencies, color='skyblue')
    plt.title('Frequencies of PowerPlays called per end')
    plt.xlabel('End')
    plt.ylabel('Frequency')
    plt.savefig('/Users/brentkong/Documents/curling/figures/graphs/Frequency_End.png')
    plt.show()
else:
    win_draw_dict = {}
    for key, value in frequency_dict.items():
        win_draw_dict[key] = (wins_dict[key] + draws_dict[key]) / (frequency_dict[key] if frequency_dict[key] != 0 else 1)
    
    categories = list(win_draw_dict.keys())
    frequencies = list(win_draw_dict.values())

    plt.figure(figsize=(8, 6))
    plt.bar(categories, frequencies, color='skyblue')
    plt.title('Win-Draw Percentage per PowerPlay called at a specific end')
    plt.xlabel('End')
    plt.ylabel('Percentage')
    plt.savefig('/Users/brentkong/Documents/curling/figures/graphs/Win_Draw_Per_End.png')
    plt.show()