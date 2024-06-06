"""
Author: Jack Beaumont
Date: 06/06/2024

This module processes video frames to create histogram images of the color
distribution.
It uses OpenCV for frame manipulation, Matplotlib for plotting histograms, and
PIL for image handling.
"""

import cv2
import time
import numpy as np
from matplotlib.figure import Figure
import io
from PIL import Image
from gui.core.constants.styles import colours
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def plot_loop(hist_queue, frame_queue, stop_event, settings):
    """
    Main loop for processing histogram data from video frames.

    Parameters:
    hist_queue (queue.Queue): Queue to store histogram images.
    frame_queue (queue.Queue): Queue to receive video frames.
    stop_event (threading.Event): Event to signal stopping the loop.
    settings (dict): Configuration settings.

    Returns:
    None
    """
    logging.info("Starting plot loop.")
    while not stop_event.is_set():
        frame, _ = frame_queue.get()
        if frame is not None:
            logging.info("Processing frame.")
            hist_image = create_histogram_image(frame)
            if hist_queue.empty():
                hist_queue.put(hist_image)
                logging.info("Histogram image put in queue.")
        time.sleep(0.1)
    logging.info("Plot loop stopped.")


def create_histogram_image(frame):
    """
    Create a histogram image from a video frame.

    Parameters:
    frame (numpy.ndarray): Video frame in BGR format.

    Returns:
    Image: Histogram image.
    """
    logging.info("Creating histogram image.")

    # Convert frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Split frame into R, G, B channels
    r, g, b = cv2.split(frame_rgb)

    # Calculate histograms for each channel
    r_hist = np.histogram(r, bins=256, range=(0, 255))[0]
    g_hist = np.histogram(g, bins=256, range=(0, 255))[0]
    b_hist = np.histogram(b, bins=256, range=(0, 255))[0]

    # Create a figure for the histogram
    fig = Figure(figsize=(4, 1), dpi=100)
    fig.set_facecolor(colours.off_black_80)
    ax = fig.add_subplot(111)
    ax.set_position([0.02, 0.1, 0.94, 0.9])  # Pack tightly
    ax.margins(x=0, y=0)

    intensity = np.arange(0, 256)

    # Plot color distribution
    ax.plot(intensity, r_hist, color="red", linewidth=0)
    ax.plot(intensity, g_hist, color="green", linewidth=0)
    ax.plot(intensity, b_hist, color="blue", linewidth=0)

    ax.fill_between(intensity, r_hist, color="red", alpha=0.5)
    ax.fill_between(intensity, g_hist, color="green", alpha=0.5)
    ax.fill_between(intensity, b_hist, color="blue", alpha=0.5)

    ax.set_facecolor(colours.off_black_80)
    ax.tick_params(axis="x", colors=colours.off_black_80)

    # Set x-axis ticks to display percentages
    ax.set_xticks(
        np.arange(0, 256, 25.5),
        [f"{i}%" for i in range(0, 101, 10)],
        color="grey",
        fontsize=8,
        y=0.1,
    )  # Divide range into 10

    ax.spines[["right", "top", "left", "bottom"]].set_visible(False)

    # Add thin grey lines for every 10th percent across the entire graph
    for i in range(0, 101, 10):
        ax.axvline(
            x=i * 255 / 100, color="grey", linestyle="--", linewidth=0.5
        )

    ax.yaxis.set_visible(False)
    ax.set_title("")

    # Save figure to a BytesIO buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)

    # Convert buffer to image
    img = Image.open(buf)
    logging.info("Histogram image created.")
    return img
