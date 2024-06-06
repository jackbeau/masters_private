"""
Author: Jack Beaumont
Date: 06/06/2024

This module provides functionality for video device management and frame
processing on macOS using OpenCV and AVFoundation.
"""

import cv2
import numpy as np
import AVFoundation
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_video_devices():
    """
    Retrieves the list of available video devices on macOS.

    Returns:
        list: A list of dictionaries containing information about each video
        device.
    """
    device_types = [
        AVFoundation.AVCaptureDeviceTypeBuiltInWideAngleCamera,
        AVFoundation.AVCaptureDeviceTypeExternal,  # Covers external cameras
    ]

    discovery_session = (
        AVFoundation.AVCaptureDeviceDiscoverySession
        .discoverySessionWithDeviceTypes_mediaType_position_(
            device_types,
            AVFoundation.AVMediaTypeVideo,
            AVFoundation.AVCaptureDevicePositionUnspecified,
        )
    )

    devices = discovery_session.devices()
    ordered_devices = []

    # Assign position indices and gather device information
    for pos, device in enumerate(devices):
        ordered_devices.append(
            {
                "localizedName": device.localizedName(),
                "uniqueID": device.uniqueID(),
                "position": pos,
            }
        )

    logging.info(f"Found video devices: {ordered_devices}")
    return ordered_devices


def get_max_resolution(device_position):
    """
    Gets the maximum resolution of the specified video device.

    Args:
        device_position (int): The position of the video device.

    Returns:
        tuple: The maximum resolution (width, height) of the video device.
    """
    cap = cv2.VideoCapture(device_position)
    if cap.isOpened():
        max_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        max_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        max_resolution = (int(max_width), int(max_height))
        cap.release()
        logging.info(
            f"Max resolution for device {device_position}: {max_resolution}"
        )
        return max_resolution
    logging.warning(
        f"Failed to open video device at position {device_position}"
    )
    return None


def filter_resolutions(max_resolution, resolution_list):
    """
    Filters a list of resolutions to match the aspect ratio and fit within the
    maximum resolution.

    Args:
        max_resolution (tuple): The maximum resolution (width, height).
        resolution_list (list): A list of resolution tuples to filter.

    Returns:
        list: A list of filtered resolutions that match the aspect ratio and
              fit within the max resolution.
    """
    aspect_ratio = int(max_resolution[0]) / int(max_resolution[1])
    filtered_resolutions = []

    for resolution in resolution_list:
        width, height = resolution
        if (
            width <= max_resolution[0]
            and height <= max_resolution[1]
            and width / height == aspect_ratio
        ):
            filtered_resolutions.append(resolution)

    logging.info(f"Filtered resolutions: {filtered_resolutions}")
    return filtered_resolutions


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
    Processes a video frame with various adjustments and transformations.

    Args:
        frame (numpy.ndarray): The input video frame.
        brightness (int): Brightness adjustment (default: 50).
        exposure (int): Exposure adjustment (default: 50).
        contrast (int): Contrast adjustment (default: 50).
        saturation (int): Saturation adjustment (default: 50).
        mirror_x (int): Horizontal mirroring (default: 0).
        mirror_y (int): Vertical mirroring (default: 0).
        clahe (int): CLAHE application flag (default: 0).
        clahe_clip_limit (int): CLAHE clip limit (default: 40).
        rotation (int): Frame rotation
                        (0, 1, 2, 3 for 0, 90, 180, 270 degrees).
        resolution (tuple): Desired output resolution (default: None).

    Returns:
        numpy.ndarray: The processed video frame.
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

    # Frame rotation
    if rotation != 0:
        adjusted_frame = rotate_frame(adjusted_frame, rotation)

    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    if clahe == 1:
        adjusted_frame = CLAHE(
            adjusted_frame, np.clip(clahe_clip_limit / 40 * 50, 1, 100)
        )

    # Adjust exposure and brightness
    if brightness != 50 or exposure != 50:
        frame_float = adjusted_frame.astype(np.float32)
        alpha = np.clip(exposure / 50, 0, 2)
        beta = np.clip((brightness / 50 - 1) * 127.5, -127, 127.5)
        adjusted_frame = cv2.convertScaleAbs(
            frame_float, alpha=alpha, beta=beta
        )

    # Adjust contrast
    if contrast != 50:
        mean_intensity = np.mean(adjusted_frame)
        contrast_factor = np.clip(contrast / 50, 0, 2)
        adjusted_frame = (
            adjusted_frame - mean_intensity
        ) * contrast_factor + mean_intensity
        adjusted_frame = np.clip(adjusted_frame, 0, 255).astype(np.uint8)

    # Adjust saturation
    if saturation != 50:
        hsv_frame = cv2.cvtColor(adjusted_frame, cv2.COLOR_BGR2HSV).astype(
            "float32"
        )
        h, s, v = cv2.split(hsv_frame)
        s = s * np.clip(saturation / 50, 0, 2)
        s = np.clip(s, 0, 255)
        hsv_frame = cv2.merge([h, s, v])
        adjusted_frame = cv2.cvtColor(
            hsv_frame.astype("uint8"), cv2.COLOR_HSV2RGB
        )
    else:
        adjusted_frame = cv2.cvtColor(
            adjusted_frame.astype("uint8"), cv2.COLOR_BGR2RGB
        )

    return adjusted_frame


def rotate_frame(frame, rotation):
    """
    Rotates the frame based on the given rotation value.

    Args:
        frame (numpy.ndarray): The input video frame.
        rotation (int): Rotation value
                        (0, 1, 2, 3 for 0, 90, 180, 270 degrees).

    Returns:
        numpy.ndarray: The rotated video frame.
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
    Applies Contrast Limited Adaptive Histogram Equalization (CLAHE)
    to the image.

    Args:
        img (numpy.ndarray): The input image.
        clipLimit (float): CLAHE clip limit.

    Returns:
        numpy.ndarray: The image with CLAHE applied.
    """
    img = cv2.cvtColor(img, cv2.COLOR_RGB2Lab)
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=(8, 8))
    img[:, :, 0] = clahe.apply(img[:, :, 0])
    img = cv2.cvtColor(img, cv2.COLOR_Lab2RGB)
    return img


def hisEqulColor(img):
    """
    Applies histogram equalization to the color image.

    Args:
        img (numpy.ndarray): The input color image.

    Returns:
        numpy.ndarray: The image with histogram equalization applied.
    """
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
    channels = cv2.split(ycrcb)
    cv2.equalizeHist(channels[0], channels[0])
    cv2.merge(channels, ycrcb)
    cv2.cvtColor(ycrcb, cv2.COLOR_YCR_CB2BGR, img)
    return img
