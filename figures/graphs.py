import matplotlib.pyplot as plt
import json

with open('/Users/brentkong/Documents/curling/figures/simulations/frequency_dict_100000.json', 'r') as f:
    data = json.load(f)

frequency_dict = data[0]
wins_dict = data[1]
loss_dict = data[2]
draws_dict = data[3]
hammer_analysis = data[4]
hammer_summary = data[5]
by_margin_raw = data[6]["by_margin"]
matches = frequency_dict.pop("matches")
mode = "win"

if mode == "frequency": 
    categories = list(frequency_dict.keys())
    frequencies = list(frequency_dict.values())

    plt.figure(figsize=(8, 6))
    plt.bar(categories, frequencies, color='skyblue')
    plt.title('Frequencies of PowerPlays called per end')
    plt.xlabel('End')
    plt.ylabel('Frequency')
    plt.savefig(f'/Users/brentkong/Documents/curling/figures/graphs/Frequency_End_{matches}.png')
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
    plt.savefig(f'/Users/brentkong/Documents/curling/figures/graphs/Win_Draw_Per_End_{matches}.png')
    plt.show()
elif mode == "win": 
    win_draw_dict = {}
    for key, value in frequency_dict.items():
        win_draw_dict[key] = (wins_dict[key]) / (frequency_dict[key] if frequency_dict[key] != 0 else 1)
    
    categories = list(win_draw_dict.keys())
    frequencies = list(win_draw_dict.values())

    plt.figure(figsize=(8, 6))
    plt.bar(categories, frequencies, color='#8dd3c7')
    plt.title('Win Percentage per PowerPlay called at a specific end')
    plt.xlabel('End')
    plt.ylabel('Percentage')
    plt.savefig(f'/Users/brentkong/Documents/curling/figures/graphs/Win_Per_End_{matches}.png')
    plt.show()
elif mode == "hammer":
    hammer_counts = hammer_analysis['hammer_start']
    no_hammer_counts = hammer_analysis['no_hammer_start']

    labels = ['Wins', 'Draws', 'Losses']

    hammer_values = [hammer_counts['wins'], hammer_counts['draws'], hammer_counts['loss']]
    no_hammer_values = [no_hammer_counts['wins'], no_hammer_counts['draws'], no_hammer_counts['loss']]
    colors = ['#8dd3c7', '#ffffb3', '#fb8072']

    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.pie(hammer_values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    plt.title('Root Team Starts with Hammer')

    plt.subplot(1, 2, 2)
    plt.pie(no_hammer_values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    plt.title('Root Team Starts without Hammer')

    plt.tight_layout()
    plt.savefig(f'/Users/brentkong/Documents/curling/figures/graphs/hammer_vs_no_hammer_pie_{matches}.png')
    plt.show()
elif mode == "by_end":
    by_margin = {int(k): int(v) for k, v in by_margin_raw.items()}

    margins = []
    for margin, count in by_margin.items():
        margins.extend([margin] * count)

    plt.figure()
    plt.hist(
        margins,
        bins=range(min(margins), max(margins) + 2),
        align="left"
    )
    plt.xlabel("Score margin after 7 ends (hammer team)")
    plt.ylabel("Frequency")
    plt.title("Histogram of Score Margin After 7 Ends (Hammer Team)")
    plt.tight_layout()
    plt.savefig(f'/Users/brentkong/Documents/curling/figures/graphs/score_margin_{matches}.png')
    plt.show()

else:
    labels = [
        "Leading after 7",
        "Tied after 7",
        "Trailing after 7"
    ]
    sizes = [
        hammer_summary["hammer_leading_after_7"],
        hammer_summary["hammer_tied_after_7"],
        hammer_summary["hammer_trailing_after_7"]
    ]

    plt.figure()
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title("End 8 Hammer Team Status After 7 Ends")
    plt.axis("equal") 
    plt.tight_layout()
    plt.savefig(f'/Users/brentkong/Documents/curling/figures/graphs/win_after_7_{matches}.png')
    plt.show()















