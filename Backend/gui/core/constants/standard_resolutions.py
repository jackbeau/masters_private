"""
Author: Jack Beaumont
Date: 06/06/2024

This module defines a list of standard resolutions in descending order and
provides functionalities to interact with these resolutions.
"""

import logging

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# List of standard resolutions in descending order
standard_resolutions = [
    (7680, 4320),
    (3840, 2160),
    (1920, 1080),
    (1280, 720),
    (640, 480),
    (640, 360),
    (128, 72),
]


def find_best_resolution(available_resolutions):
    """
    Find the best standard resolution that matches one of the available
    resolutions.

    Parameters:
    available_resolutions (list of tuple): A list of available resolution
    tuples (width, height).

    Returns:
    tuple: The best matching resolution or None if no match is found.
    """
    logging.info("Finding the best matching resolution.")
    for standard_resolution in standard_resolutions:
        if standard_resolution in available_resolutions:
            logging.info(f"Match found: {standard_resolution}")
            return standard_resolution
    logging.info("No matching resolution found.")
    return None


def is_standard_resolution(resolution):
    """
    Check if the given resolution is a standard resolution.

    Parameters:
    resolution (tuple): A resolution tuple (width, height).

    Returns:
    bool: True if the resolution is a standard resolution, False otherwise.
    """
    logging.info(f"Checking if {resolution} is a standard resolution.")
    return resolution in standard_resolutions


def add_custom_resolution(resolutions_list, resolution):
    """
    Add a custom resolution to the list if it's not already present.

    Parameters:
    resolutions_list (list of tuple): The list of resolution tuples
                                      (width, height).
    resolution (tuple): A resolution tuple to add (width, height).

    Returns:
    list of tuple: The updated list of resolutions.
    """
    if resolution not in resolutions_list:
        resolutions_list.append(resolution)
        logging.info(f"Added custom resolution: {resolution}")
    else:
        logging.info(f"Resolution {resolution} is already in the list.")
    return resolutions_list


def remove_custom_resolution(resolutions_list, resolution):
    """
    Remove a custom resolution from the list if it exists.

    Parameters:
    resolutions_list (list of tuple): The list of resolution tuples
                                      (width, height).
    resolution (tuple): A resolution tuple to remove (width, height).

    Returns:
    list of tuple: The updated list of resolutions.
    """
    if resolution in resolutions_list:
        resolutions_list.remove(resolution)
        logging.info(f"Removed custom resolution: {resolution}")
    else:
        logging.info(f"Resolution {resolution} is not in the list.")
    return resolutions_list
