import cv2 
import numpy as np
import cv2 
import numpy as np
import AVFoundation
import objc

# Note this code will only work on macOS

# NSBundle = objc.loadBundle('AVFoundation', globals(), bundle_path='/System/Library/Frameworks/AVFoundation.framework')

def get_video_devices():
    device_types = [
        AVFoundation.AVCaptureDeviceTypeBuiltInWideAngleCamera,
        AVFoundation.AVCaptureDeviceTypeExternal,  # This can be used to cover other external cameras
    ]

    discovery_session = AVFoundation.AVCaptureDeviceDiscoverySession.discoverySessionWithDeviceTypes_mediaType_position_(
        device_types,
        AVFoundation.AVMediaTypeVideo,
        AVFoundation.AVCaptureDevicePositionUnspecified
    )

    devices = discovery_session.devices()
    ordered_devices = []

    # built_in_wide_angle_cameras = []
    # external_cameras = []
    
    # for pos, device in enumerate(devices):
    #     info = {
    #         "localizedName": device.localizedName(),
    #         "uniqueID": device.uniqueID(),
    #         "position": None  # Position will be assigned later
    #     }
        


    #     if device.deviceType() == AVFoundation.AVCaptureDeviceTypeBuiltInWideAngleCamera:
    #         built_in_wide_angle_cameras.append(info)
    #     elif device.deviceType() == AVFoundation.AVCaptureDeviceTypeExternal:
    #         external_cameras.append(info)

    # # Combine the lists in the desired order
    # ordered_devices = built_in_wide_angle_cameras + external_cameras
    
    # Assign position indices
    for pos, device in enumerate(devices):
        ordered_devices.append( {
            "localizedName": device.localizedName(),
            "uniqueID": device.uniqueID(),
            "position": pos
        })

    print(ordered_devices)
    return ordered_devices
      
def get_max_resolution(device_position):
    # Get available max resolution for video device
    cap = cv2.VideoCapture(device_position)
    if cap.isOpened():
        max_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        max_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        max_resolution = (int(max_width), int(max_height))
        cap.release()
        return max_resolution


def filter_resolutions(max_resolution, resolution_list):
    aspect_ratio = int(max_resolution[0]) / int(max_resolution[1])
    filtered_resolutions = []

    for resolution in resolution_list:
        width, height = resolution
        if width <= max_resolution[0] and height <= max_resolution[1] and width / height == aspect_ratio:
            filtered_resolutions.append(resolution)

    return filtered_resolutions

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
        adjusted_frame = cv2.cvtColor(hsv_frame.astype("uint8"), cv2.COLOR_HSV2RGB)
    else:
        adjusted_frame = cv2.cvtColor(adjusted_frame.astype("uint8"), cv2.COLOR_BGR2RGB)
        
    # Convert back to BGR color space
    
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
    img = cv2.cvtColor(img, cv2.COLOR_RGB2Lab)
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=(8,8))
    #0 to 'L' channel, 1 to 'a' channel, and 2 to 'b' channel
    img[:,:,0] = clahe.apply(img[:,:,0])
    img = cv2.cvtColor(img, cv2.COLOR_Lab2RGB)
    return img

def hisEqulColor(img):
    ycrcb=cv2.cvtColor(img,cv2.COLOR_BGR2YCR_CB)
    channels=cv2.split(ycrcb)
    cv2.equalizeHist(channels[0],channels[0])
    cv2.merge(channels,ycrcb)
    cv2.cvtColor(ycrcb,cv2.COLOR_YCR_CB2BGR,img)
    return img
