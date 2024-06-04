import numpy as np
import cv2
import logging

logger = logging.getLogger(__name__)

def compute_homography_matrix(src_points, dst_points):
    homography_matrix, _ = cv2.findHomography(np.array(src_points), np.array(dst_points))
    return homography_matrix

def apply_homography(point, homography_matrix):
    point_homogeneous = np.append(point, 1)
    transformed_point = np.dot(homography_matrix, point_homogeneous)
    transformed_point /= transformed_point[2]
    logger.debug(f"Transformed point {point} to {transformed_point[:2]}")
    return transformed_point[:2]

def seg_to_bbox(mask):
    x_coords, y_coords = mask[:, 0], mask[:, 1]
    return np.min(x_coords), np.min(y_coords), np.max(x_coords), np.max(y_coords)

def get_lowest_point(bbox):
    x1, y1, x2, y2 = bbox
    lowest_point = np.array([int((x1 + x2) / 2), y2])
    logger.debug(f"Lowest point for bbox {bbox}: {lowest_point}")
    return lowest_point
