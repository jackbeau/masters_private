"""
Author: Jack Beaumont
Date: 06/06/2024

This module provides functions for computing homography matrices, applying
transformations,
and extracting key points from masks and bounding boxes.
"""

import numpy as np
import cv2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_homography_matrix(src_points, dst_points):
    """
    Compute the homography matrix from source points to destination points.

    Parameters:
    src_points (list of list of float): List of source points.
    dst_points (list of list of float): List of destination points.

    Returns:
    np.ndarray: Homography matrix.
    """
    homography_matrix, _ = cv2.findHomography(
        np.array(src_points), np.array(dst_points)
    )
    logger.info("Computed homography matrix")
    return homography_matrix


def apply_homography(point, homography_matrix):
    """
    Apply the homography matrix to a point.

    Parameters:
    point (list or np.ndarray): The point to be transformed.
    homography_matrix (np.ndarray): The homography matrix.

    Returns:
    np.ndarray: Transformed point as a 2D coordinate.
    """
    point_homogeneous = np.append(point, 1)
    transformed_point = np.dot(homography_matrix, point_homogeneous)
    transformed_point /= transformed_point[2]
    logger.debug(f"Transformed point {point} to {transformed_point[:2]}")
    return transformed_point[:2]


def seg_to_bbox(mask):
    """
    Convert a segmentation mask to a bounding box.

    Parameters:
    mask (np.ndarray): Segmentation mask with coordinates.

    Returns:
    tuple: Bounding box as (min_x, min_y, max_x, max_y).
    """
    x_coords, y_coords = mask[:, 0], mask[:, 1]
    bbox = (
        np.min(x_coords),
        np.min(y_coords),
        np.max(x_coords),
        np.max(y_coords),
    )
    logger.info(f"Converted segmentation mask to bbox: {bbox}")
    return bbox


def get_lowest_point(bbox):
    """
    Get the lowest point of a bounding box.

    Parameters:
    bbox (tuple): Bounding box as (min_x, min_y, max_x, max_y).

    Returns:
    np.ndarray: Lowest point as a 2D coordinate.
    """
    x1, y1, x2, y2 = bbox
    lowest_point = np.array([int((x1 + x2) / 2), y2])
    logger.debug(f"Lowest point for bbox {bbox}: {lowest_point}")
    return lowest_point


def get_center_point(bbox):
    """
    Get the center point of a bounding box.

    Parameters:
    bbox (tuple): Bounding box as (min_x, min_y, max_x, max_y).

    Returns:
    np.ndarray: Center point as a 2D coordinate.
    """
    x1, y1, x2, y2 = bbox
    center_point = np.array([int((x1 + x2) / 2), int((y1 + y2) / 2)])
    logger.debug(f"Center point for bbox {bbox}: {center_point}")
    return center_point
