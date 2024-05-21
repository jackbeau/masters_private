import cv2
import time
import numpy as np
from matplotlib.figure import Figure
import io
from PIL import Image
from gui.core.constants.styles import colours

def plot_loop(hist_queue, frame_queue, stop_event, settings):
    """Main loop for processing histogram data."""
    while not stop_event.is_set():
        frame = frame_queue.get()
        if frame is not None:
            hist_image = create_histogram_image(frame)
            if hist_queue.empty():
                hist_queue.put(hist_image)
        time.sleep(0.1)

def create_histogram_image(frame):
    """Create a histogram image from the frame."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    r, g, b = cv2.split(frame_rgb)
    r_hist = np.histogram(r, bins=256, range=(0, 255))[0]
    g_hist = np.histogram(g, bins=256, range=(0, 255))[0]
    b_hist = np.histogram(b, bins=256, range=(0, 255))[0]

    fig = Figure(figsize=(4, 1), dpi=100)
    fig.set_facecolor(colours.off_black_80)
    ax = fig.add_subplot(111)
    ax.set_position([.02, .1, .94, .9])  # pack tightly
    ax.margins(x=0, y=0)

    intensity = np.arange(0, 256)
    # Plot color distribution
    ax.plot(intensity, np.histogram(r, bins=256, range=(0, 255))[
            0], color='red', linewidth=0)
    ax.plot(intensity, np.histogram(g, bins=256, range=(0, 255))[
            0], color='green', linewidth=0)
    ax.plot(intensity, np.histogram(b, bins=256, range=(0, 255))[
            0], color='blue', linewidth=0)

    ax.fill_between(intensity, np.histogram(
        r, bins=256, range=(0, 255))[0], color='red', alpha=0.5)
    ax.fill_between(intensity, np.histogram(
        g, bins=256, range=(0, 255))[0], color='green', alpha=0.5)
    ax.fill_between(intensity, np.histogram(
        b, bins=256, range=(0, 255))[0], color='blue', alpha=0.5)

    ax.set_facecolor(colours.off_black_80)
    ax.tick_params(axis='x', colors=colours.off_black_80)

    # Set x-axis ticks to display percentages
    ax.set_xticks(np.arange(0, 256, 25.5),
                    [f"{i}%" for i in range(0, 101, 10)],
                    color='grey', fontsize=8, y=0.1)  # divide range into 10

    ax.spines[['right', 'top', 'left', 'bottom']].set_visible(False)

    # Add thin grey lines for every 10th percent across the entire graph
    for i in range(0, 101, 10):
        ax.axvline(x=i * 255 / 100, color='grey',
                    linestyle='--', linewidth=0.5)

    ax.yaxis.set_visible(False)
    ax.set_title('')

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    return img
