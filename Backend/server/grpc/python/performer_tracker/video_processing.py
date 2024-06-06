"""
Author: Jack Beaumont
Date: 06/06/2024

This module provides functions for processing video frames, including
adjusting brightness, exposure, contrast, saturation, mirroring, rotating,
applying CLAHE (Contrast Limited Adaptive Histogram Equalization), and
cropping.
"""

import cv2
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_frame(
    frame,
    brightness=50,
    exposure=50,
    contrast=50,
    saturation=50,
    mirror_x=0,
    mirror_y=0,
    clahe=0,
    clahe_clip_limit=40,
    rotation=0,
    resolution=None,
):
    """
    Process a single video frame by applying various adjustments.

    Parameters:
    - frame: The input video frame to process (numpy array).
    - brightness: Brightness adjustment (0-100, default is 50).
    - exposure: Exposure adjustment (0-100, default is 50).
    - contrast: Contrast adjustment (0-100, default is 50).
    - saturation: Saturation adjustment (0-100, default is 50).
    - mirror_x: Mirror frame horizontally if set to 1 (default is 0).
    - mirror_y: Mirror frame vertically if set to 1 (default is 0).
    - clahe: Apply CLAHE if set to 1 (default is 0).
    - clahe_clip_limit: Clip limit for CLAHE (default is 40).
    - rotation: Rotate frame
                (0-3, corresponding to 0°, 90°, 180°, 270°, default is 0).
    - resolution: Tuple for desired resolution (width, height),
                  default is None.

    Returns:
    - adjusted_frame: The processed video frame (numpy array).
    """

    # Frame mirroring
    if mirror_x == 1 and mirror_y == 1:
        adjusted_frame = cv2.flip(frame, -1)
    elif mirror_x == 1:
        adjusted_frame = cv2.flip(frame, 1)
    elif mirror_y == 1:
        adjusted_frame = cv2.flip(frame, 0)
    else:
        adjusted_frame = frame

    # Resolution reduction
    if resolution is not None:
        adjusted_frame = cv2.resize(
            adjusted_frame, resolution, interpolation=cv2.INTER_AREA
        )
        logger.info(f"Frame resized to {resolution}")

    # Frame rotation
    if rotation != 0:
        adjusted_frame = rotate_frame(adjusted_frame, rotation)
        logger.info(f"Frame rotated by {rotation * 90} degrees")

    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    if clahe == 1:
        adjusted_frame = CLAHE(
            adjusted_frame, np.clip(clahe_clip_limit / 40 * 50, 1, 100)
        )
        logger.info(f"CLAHE applied with clip limit {clahe_clip_limit}")

    # Adjust exposure and brightness
    if (brightness != 50) or (exposure != 50):
        frame_float = adjusted_frame.astype(np.float32)
        alpha = np.clip(exposure / 50, 0, 2)
        beta = np.clip((brightness / 50 - 1) * 127.5, -127, 127.5)
        adjusted_frame = cv2.convertScaleAbs(
            frame_float, alpha=alpha, beta=beta
        )
        logger.info(
            f"Brightness adjusted to {brightness}, "
            f"Exposure adjusted to {exposure}"
        )

    # Adjust contrast
    if contrast != 50:
        mean_intensity = np.mean(adjusted_frame)
        contrast_factor = np.clip(contrast / 50, 0, 2)
        adjusted_frame = (
            adjusted_frame - mean_intensity
        ) * contrast_factor + mean_intensity
        adjusted_frame = np.clip(adjusted_frame, 0, 255).astype(np.uint8)
        logger.info(f"Contrast adjusted to {contrast}")

    # Adjust saturation
    if saturation != 50:
        hsv_frame = cv2.cvtColor(adjusted_frame, cv2.COLOR_BGR2HSV).astype(
            "float32"
        )
        (h, s, v) = cv2.split(hsv_frame)
        s = s * np.clip(saturation / 50, 0, 2)
        s = np.clip(s, 0, 255)
        hsv_frame = cv2.merge([h, s, v])
        adjusted_frame = cv2.cvtColor(
            hsv_frame.astype("uint8"), cv2.COLOR_HSV2BGR
        )
        logger.info(f"Saturation adjusted to {saturation}")

    return adjusted_frame


def rotate_frame(frame, rotation):
    """
    Rotate the input frame by 90, 180, or 270 degrees.

    Parameters:
    - frame: The input video frame to rotate (numpy array).
    - rotation: Integer representing the rotation
                (0=0°, 1=90° clockwise, 2=180°, 3=90° counterclockwise).

    Returns:
    - rotated_frame: The rotated video frame (numpy array).
    """
    if rotation == 0:
        return frame
    elif rotation == 1:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif rotation == 2:
        return cv2.rotate(frame, cv2.ROTATE_180)
    elif rotation == 3:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)


def CLAHE(img, clipLimit):
    """
    Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) to the
    input image.

    Parameters:
    - img: The input image (numpy array).
    - clipLimit: Clip limit for CLAHE.

    Returns:
    - clahe_img: The image after applying CLAHE (numpy array).
    """
    img = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=(8, 8))
    img[:, :, 0] = clahe.apply(img[:, :, 0])
    img = cv2.cvtColor(img, cv2.COLOR_Lab2BGR)
    return img


def crop_frame(frame, crop_points):
    """
    Crop the input frame to the region of interest defined by crop_points.

    Parameters:
    - frame: The input video frame to crop (numpy array).
    - crop_points: List of points defining the region of interest.

    Returns:
    - cropped_frame: The cropped video frame (numpy array).
    """
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    roi_corners = np.array([crop_points], dtype=np.int32)
    cv2.fillPoly(mask, roi_corners, 255)
    cropped_frame = cv2.bitwise_and(frame, frame, mask=mask)

    # Find bounding box around the ROI
    x, y, w, h = cv2.boundingRect(roi_corners)
    cropped_frame = cropped_frame[y: y + h, x: x + w]

    logger.info(f"Frame cropped to region defined by {crop_points}")

    return cropped_frame
