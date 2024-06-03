import time
import cv2
import gui.pages.shared.video_utils

def video_loop(frame_queue, stop_event, settings):
    print("Starting video loop")
    video_device = settings.get('video_device_pos', 0)
    stream = cv2.VideoCapture(video_device)

    while not stop_event.is_set():
        resolution = settings.get('resolution', (640, 480))
        rotation = settings.get('rotation', 0)
        mirror_x = settings.get('mirror_x', 0)
        mirror_y = settings.get('mirror_y', 0)
        clahe = settings.get('clahe', 0)
        clahe_clip_limit = settings.get('clahe_clip_limit', 40)
        brightness = settings.get('brightness', 50)
        exposure = settings.get('exposure', 50)
        contrast = settings.get('contrast', 50)
        saturation = settings.get('saturation', 50)

        ret, frame = stream.read()
        if ret:
            frame = gui.pages.shared.video_utils.process_frame(
                frame,
                brightness=brightness,
                exposure=exposure,
                contrast=contrast,
                saturation=saturation,
                mirror_x=mirror_x,
                mirror_y=mirror_y,
                clahe=clahe,
                clahe_clip_limit=clahe_clip_limit,
                rotation=rotation,
                resolution=resolution
            )
            frame = resize_frame_for_canvas(frame)
            if not stop_event.is_set():  # Add this check before putting frame into the queue
                frame_queue.put(frame)
            time.sleep(0.001)
        else:
            frame = cv2.imread("gui/assets/no_input.png")
            frame = resize_frame_for_canvas(frame)
            if not stop_event.is_set():  # Add this check before putting frame into the queue
                frame_queue.put(frame)
            time.sleep(1)
            print("No frame captured")
    stream.release()
    print("Stopping video loop")

def resize_frame_for_canvas(frame):
    h, w = frame.shape[:2]
    scaling_factor = min(600 / w, 340 / h)
    new_width = int(w * scaling_factor)
    new_height = int(h * scaling_factor)
    frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return frame