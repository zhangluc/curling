import matplotlib.pyplot as plt
import json

with open('/Users/brentkong/Documents/curling/figures/simulations/frequency_dict_1000_new.json', 'r') as f:
    data = json.load(f)

frequency_dict = data[0]
wins_dict = data[1]
loss_dict = data[2]
draws_dict = data[3]
hammer_analysis = data[4]
matches = frequency_dict.pop("matches")
mode = "hammer"

if mode == "frequency": 
    categories = list(frequency_dict.keys())
    frequencies = list(frequency_dict.values())

    plt.figure(figsize=(8, 6))
    plt.bar(categories, frequencies, color='skyblue')
    plt.title('Frequencies of PowerPlays called per end')
    plt.xlabel('End')
    plt.ylabel('Frequency')
    plt.savefig(f'/Users/brentkong/Documents/curling/figures/graphs/Frequency_End_{matches}_new.png')
    plt.show()
elif mode == "win-draw": 
    win_draw_dict = {}
    for key, value in frequency_dict.items():
        win_draw_dict[key] = (wins_dict[key] + draws_dict[key]) / (frequency_dict[key] if frequency_dict[key] != 0 else 1)
    
    categories = list(win_draw_dict.keys())
    frequencies = list(win_draw_dict.values())

    plt.figure(figsize=(8, 6))
    plt.bar(categories, frequencies, color='#8dd3c7')
    plt.title('Win-Draw Percentage per PowerPlay called at a specific end')
    plt.xlabel('End')
    plt.ylabel('Percentage')
    plt.savefig(f'/Users/brentkong/Documents/curling/figures/graphs/Win_Draw_Per_End_{matches}_new.png')
    plt.show()
else:
    hammer_counts = hammer_analysis['hammer_start']
    no_hammer_counts = hammer_analysis['no_hammer_start']

    labels = ['Wins', 'Draws', 'Losses']

    hammer_values = [hammer_counts['wins'], hammer_counts['draws'], hammer_counts['losses']]
    no_hammer_values = [no_hammer_counts['wins'], no_hammer_counts['draws'], no_hammer_counts['losses']]
    colors = ['#8dd3c7', '#ffffb3', '#fb8072']

    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.pie(hammer_values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    plt.title('Root Team Starts with Hammer')

    plt.subplot(1, 2, 2)
    plt.pie(no_hammer_values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    plt.title('Root Team Starts without Hammer')

    plt.tight_layout()
    plt.savefig(f'/Users/brentkong/Documents/curling/figures/graphs/hammer_vs_no_hammer_pie_{matches}_new.png')
    plt.show()