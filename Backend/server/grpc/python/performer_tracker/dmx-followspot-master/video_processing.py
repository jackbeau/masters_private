import cv2
import numpy as np

def process_frame(frame, brightness=50, exposure=50, contrast=50, saturation=50, mirror_x=0, mirror_y=0, clahe=0, clahe_clip_limit=40, rotation=0, resolution=None):
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
        adjusted_frame = cv2.resize(adjusted_frame, resolution, interpolation=cv2.INTER_AREA)

    # Frame rotation
    if rotation != 0:
        adjusted_frame = rotate_frame(adjusted_frame, rotation)

    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    if clahe == 1:
        adjusted_frame = CLAHE(adjusted_frame, np.clip(clahe_clip_limit/40*50, 1, 100))
    
    # Adjust exposure and brightness
    if (brightness != 50) or (exposure != 50):
        frame_float = adjusted_frame.astype(np.float32)
        alpha = np.clip(exposure / 50, 0, 2)
        beta = np.clip((brightness / 50 - 1) * 127.5, -127, 127.5)
        adjusted_frame = cv2.convertScaleAbs(frame_float, alpha=alpha, beta=beta)
    
    if contrast != 50:
        # Compute the mean intensity of the frame
        mean_intensity = np.mean(adjusted_frame)
        
        # Adjust contrast
        contrast_factor = np.clip(contrast / 50, 0, 2)
        adjusted_frame = (adjusted_frame - mean_intensity) * contrast_factor + mean_intensity
        
        # Clip pixel values to ensure they are within the valid range [0, 255]
        adjusted_frame = np.clip(adjusted_frame, 0, 255).astype(np.uint8)
    
    if saturation != 50:
        # Convert to HSV color space
        hsv_frame = cv2.cvtColor(adjusted_frame, cv2.COLOR_BGR2HSV).astype("float32")

        # Adjust saturation
        (h, s, v) = cv2.split(hsv_frame)
        s = s * np.clip(saturation / 50, 0, 2)
        s = np.clip(s, 0, 255)
        hsv_frame = cv2.merge([h, s, v])
        adjusted_frame = cv2.cvtColor(hsv_frame.astype("uint8"), cv2.COLOR_HSV2BGR)

    return adjusted_frame

def rotate_frame(frame, rotation):
    if rotation == 0:
        return frame
    elif rotation == 1:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif rotation == 2:
        return cv2.rotate(frame, cv2.ROTATE_180)
    elif rotation == 3:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

def CLAHE(img, clipLimit):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=(8,8))
    img[:,:,0] = clahe.apply(img[:,:,0])
    img = cv2.cvtColor(img, cv2.COLOR_Lab2BGR)
    return img

def crop_frame(frame, crop_points):
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    roi_corners = np.array([crop_points], dtype=np.int32)
    cv2.fillPoly(mask, roi_corners, 255)
    cropped_frame = cv2.bitwise_and(frame, frame, mask=mask)

    # Find bounding box around the ROI
    x, y, w, h = cv2.boundingRect(roi_corners)
    cropped_frame = cropped_frame[y:y+h, x:x+w]
    
    return cropped_frame