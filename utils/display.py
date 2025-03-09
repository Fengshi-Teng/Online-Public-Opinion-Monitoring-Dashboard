import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

def display_rose_chart(emotion_score: dict):
    """
    Display a 'rose chart' (polar bar chart) of emotion scores,
    where each bar's color intensity depends on the bar's value.

    Parameters
    ----------
    emotion_score : dict
        A dictionary where keys are emotion names and values are numeric scores.
        Example:
            {
                "joy": 25,
                "sadness": 30,
                "anger": 15,
                "fear": 10,
                "surprise": 20,
                "disgust": 10
            }
    """

    plt.style.use("seaborn-v0_8-whitegrid")   # use a cleaner style

    labels = list(emotion_score.keys())
    vals = np.array(list(emotion_score.values()), dtype=float)
    num_vars = len(labels)

    # Get angles from 0 to 2π, one per emotion
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)
    width = 2 * np.pi / num_vars

    # Create a polar subplot
    fig, ax = plt.subplots(subplot_kw={"polar": True}, figsize=(6, 6))
    fig.subplots_adjust(top=0.90, bottom=0.05)

    # 1) Pick a color map. 'Blues' goes from light blue to dark blue.
    #    You can try "Reds", "Greens", "PuBuGn", etc. for different color families.
    cmap = cm.get_cmap("Blues")  

    # 2) Normalize each bar value to [0..1], then pick a color based on that ratio
    max_val = vals.max()
    if max_val == 0:
        # avoid division by zero if all values are 0
        normalized = np.zeros_like(vals)
    else:
        normalized = vals / max_val

    # 3) Generate a list of RGBA colors. Higher value => darker shade.
    bar_colors = [cmap(norm) for norm in normalized]

    # Create the bars
    bars = ax.bar(
        angles,
        vals,
        width=width,
        color=bar_colors,
        edgecolor="white",
        linewidth=1.5,
        alpha=0.9
    )

    # Set the angle/label for each bar
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=11, fontweight="bold")
    ax.tick_params(axis='x', pad=15)

    # Hide the outer polar spine
    ax.spines["polar"].set_visible(False)

    # Rotate so the first bar starts at the top (π/2) rather than the right (0)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Optionally set radial limits or remove radial labels
    # ax.set_yticks([5, 10, 15, 20, 25, 30])
    # ax.set_yticklabels(["5", "10", "15", "20", "25", "30"])

    # Add numeric labels on each bar
    for bar, val in zip(bars, vals):
        angle = bar.get_x() + bar.get_width() / 2
        # Slight offset outward from the bar end
        offset = 1.05
        # Place the text in polar coords: (radius=val * offset, angle=angle)
        ax.text(
            angle,
            val * offset,
            f"{int(val)}",
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="black",
            rotation_mode="anchor"
        )

    # Title
    ax.set_title("Emotion Distribution (Gradient by Proportion)", y=1.08, fontsize=14, fontweight="bold")

    return plt


from wordcloud import WordCloud
from io import BytesIO
from PIL import Image


def generate_wordcloud_from_text(text: str):
    # Make sure we have text
    if not text:
        return None

    # Create a WordCloud
    wc = WordCloud(
        background_color="white",
        width=1200,      # Increase width
        height=800,      # Increase height
        scale=2,         # or use a scale factor
        max_words=200
    ).generate(text)
   
    # Convert to PIL image (or you can directly return 'wc' if you like)
    return wc.to_image()

def generate_wordcloud_from_dict(freq_dict: dict):
    # Make sure we have a dictionary
    if not freq_dict:
        return None
    # 1) Create a WordCloud instance
    wc = WordCloud(
        background_color="white",
        width=1200,      # Increase width
        height=800,      # Increase height
        scale=2,         # or use a scale factor
        max_words=200
    ).generate_from_frequencies(freq_dict)
    # 3) Convert to PIL image (or you can directly return 'wc' if you like)
    return wc.to_image()

# test = {
#     "joy": 20,
#     "sadness": 30,
#     "anger": 15,
#     "fear": 10,
#     "surprise": 15,
#     "disgust": 10
# }

# display_rose_chart(test)

