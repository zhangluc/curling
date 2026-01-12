import json
from pathlib import Path
import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
    "axes.titleweight": "semibold",
    "font.size": 11,
})

COLORS = {
    "frequency_bar": "#6BAED6",   
    "win":           "#2171B5",   
    "draw":          "#41AB5D",   

    "leading": "#2A9D8F", 
    "tied": "#E9C46A",
    "trailing": "#E76F51",
}


def finish_plot(save_path: Path):
    plt.tight_layout()
    plt.savefig(save_path)
    plt.show()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIMULATIONS_DIR = PROJECT_ROOT / "figures" / "simulations"
SAVE_DIR = PROJECT_ROOT / "figures" / "graphs"

with open(SIMULATIONS_DIR / "frequency_dict_100000.json", "r") as f:
    data = json.load(f)

frequency_dict = data[0]
wins_dict = data[1]
draws_dict = data[3]
hammer_summary_6 = data[5]
hammer_summary_7 = data[7]
hammer_summary_8 = data[9]
matches = frequency_dict.pop("matches")





categories = list(frequency_dict.keys())
frequencies = list(frequency_dict.values())
plt.figure(figsize=(9, 6))
plt.bar(categories, frequencies, color=COLORS["frequency_bar"], edgecolor="white", linewidth=0.8)
plt.title("Frequencies of PowerPlays Called per End")
plt.xlabel("End")
plt.ylabel("Frequency")
finish_plot(SAVE_DIR / f"Frequency_End_{matches}.png")





win_percent = {}
draw_percent = {}
for key in frequency_dict:
    total = frequency_dict[key] if frequency_dict[key] != 0 else 1
    win_percent[key] = wins_dict[key] / total
    draw_percent[key] = draws_dict[key] / total

categories = list(win_percent.keys())
win_vals = [win_percent[k] for k in categories]
draw_vals = [draw_percent[k] for k in categories]

plt.figure(figsize=(9, 6))
plt.bar(categories, win_vals, label="Win %", color=COLORS["win"], edgecolor="white", linewidth=0.8)
plt.bar(categories, draw_vals, bottom=win_vals, label="Draw %", color=COLORS["draw"], edgecolor="white", linewidth=0.8)
plt.title("Win and Draw Percentage per PowerPlay Called at Each End")
plt.xlabel("End")
plt.ylabel("Percentage")
plt.legend(frameon=False)
finish_plot(SAVE_DIR / f"Win_Draw_Stacked_Per_End_{matches}.png")





def plot_status_pie(title: str, sizes: list, save_name: str):
    labels = ["Leading", "Tied", "Trailing"]
    pie_colors = [COLORS["leading"], COLORS["tied"], COLORS["trailing"]]

    plt.figure(figsize=(7, 6))
    plt.pie(
        sizes,
        labels=labels,
        colors=pie_colors,
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1.0},
        textprops={"color": "#222222"},
    )
    plt.title(title)
    plt.axis("equal")
    finish_plot(SAVE_DIR / save_name)

plot_status_pie(
    "End 6 Hammer Team Status After 5 Ends",
    [
        hammer_summary_6["caller_leading_after_5"],
        hammer_summary_6["caller_tied_after_5"],
        hammer_summary_6["caller_trailing_after_5"],
    ],
    f"win_after_5_{matches}.png",
)

plot_status_pie(
    "End 7 Hammer Team Status After 6 Ends",
    [
        hammer_summary_7["caller_leading_after_6"],
        hammer_summary_7["caller_tied_after_6"],
        hammer_summary_7["caller_trailing_after_6"],
    ],
    f"win_after_6_{matches}.png",
)

plot_status_pie(
    "End 8 Hammer Team Status After 7 Ends",
    [
        hammer_summary_8["caller_leading_after_7"],
        hammer_summary_8["caller_tied_after_7"],
        hammer_summary_8["caller_trailing_after_7"],
    ],
    f"win_after_7_{matches}.png",
)
