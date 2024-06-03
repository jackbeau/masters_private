import cv2
import logging
import os
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from collections import defaultdict, deque
import uuid
import numpy as np
from config.settings import (
    CAMERA_ID, SAVE_INTERVAL, USER_FOLDER, UNCERTAIN_FOLDER,
    LIGHT_NODE_IP, LIGHT_NODE_PORT, LIGHT_UNIVERSE_ID, MAX_PAN, MAX_TILT, KP,
    SHOW_WINDOW, LOGGING_LEVEL
)
from utils.homography import apply_homography, seg_to_bbox, get_lowest_point, homography_matrix
from reid.reid_model import extract_reid_features, load_database, match_descriptors
from light_control.controller import LightController
from light_control.pan_tilt_calculator import PanTiltCalculator, LightPositionUpdater

# Setup logging
logging.basicConfig(level=getattr(logging, LOGGING_LEVEL.upper()))
logger = logging.getLogger(__name__)

async def start_camera_stream():
    logger.info("Starting camera stream")
    # Load YOLO model
    model = YOLO("yolov8n-seg.pt")

    # Initialize webcam
    cap = cv2.VideoCapture(CAMERA_ID)
    frame_count = 0
    yolo_id_to_user = {}
    track_histories = defaultdict(lambda: deque(maxlen=10))
    user_colors = {}

    # Ensure directories exist
    os.makedirs(USER_FOLDER, exist_ok=True)
    os.makedirs(UNCERTAIN_FOLDER, exist_ok=True)

    database = load_database(USER_FOLDER)
    uncertain_database = load_database(UNCERTAIN_FOLDER)

    # Light controller initialization
    light_controller = LightController(LIGHT_NODE_IP, LIGHT_NODE_PORT, LIGHT_UNIVERSE_ID)
    light_controller.add_channel('pan', start=1)
    light_controller.add_channel('tilt', start=2)
    light_controller.add_channel('shutter', start=4)
    light_controller.add_channel('dimmer', start=5)
    current_pan, current_tilt = 0, 0

    while True:
        ret, im0 = cap.read()
        if not ret:
            logger.error("Video feed is empty, no frame found.")
            break

        annotator = Annotator(im0.copy(), line_width=2)
        results = model.track(source=im0, persist=True)

        if results[0].boxes.id is not None and results[0].masks is not None:
            masks = results[0].masks.xy
            track_ids = results[0].boxes.id.int().cpu().tolist()

            for mask, track_id in zip(masks, track_ids):
                x1, y1, x2, y2 = seg_to_bbox(mask)
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                if x1 < 0 or y1 < 0 or x2 >= im0.shape[1] or y2 >= im0.shape[0]:
                    continue

                person_image = im0[y1:y2, x1:x2]

                if person_image.size == 0:
                    continue

                descriptors = extract_reid_features(person_image)
                label = f'ID: {track_id} - Not Identified'

                if descriptors is not None and descriptors.size > 0:
                    match_id, score = match_descriptors(descriptors, database, threshold=15)

                    if match_id:
                        user_folder = os.path.join(USER_FOLDER, match_id)
                        os.makedirs(user_folder, exist_ok=True)

                        if frame_count % SAVE_INTERVAL == 0:
                            img_name = f'{uuid.uuid4()}.jpg'
                            img_path = os.path.join(user_folder, img_name)
                            cv2.imwrite(img_path, person_image)

                        track_histories[track_id].append((match_id, score))
                    else:
                        uncertain_match_id, uncertain_score = match_descriptors(descriptors, uncertain_database, threshold=20)

                        if uncertain_match_id:
                            uncertain_user_folder = os.path.join(UNCERTAIN_FOLDER, uncertain_match_id)
                            os.makedirs(uncertain_user_folder, exist_ok=True)
                            img_name = f'{uuid.uuid4()}.jpg'
                            img_path = os.path.join(uncertain_user_folder, img_name)
                            cv2.imwrite(img_path, person_image)

                            track_histories[track_id].append((uncertain_match_id, uncertain_score))
                        else:
                            new_uncertain_id = f'uncertain_{len(os.listdir(UNCERTAIN_FOLDER))}'
                            new_uncertain_folder = os.path.join(UNCERTAIN_FOLDER, new_uncertain_id)
                            os.makedirs(new_uncertain_folder, exist_ok=True)
                            img_name = f'{uuid.uuid4()}.jpg'
                            img_path = os.path.join(new_uncertain_folder, img_name)
                            cv2.imwrite(img_path, person_image)
                            uncertain_database[new_uncertain_id] = [descriptors]

                            track_histories[track_id].append((new_uncertain_id, uncertain_score))

                if len(track_histories[track_id]) > 0:
                    id_counts = defaultdict(int)
                    for id, score in track_histories[track_id]:
                        id_counts[id] += 1
                    best_match_id = max(id_counts, key=id_counts.get)
                    match_percentage = (id_counts[best_match_id] / len(track_histories[track_id])) * 100
                    best_score = min(score for id, score in track_histories[track_id] if id == best_match_id)
                    label = f'ID: {track_id} - {best_match_id} ({match_percentage:.2f}%) Score: {best_score:.2f}'

                    yolo_id_to_user[track_id] = best_match_id
                    user_colors[best_match_id] = colors(len(user_colors), True)

                annotator.box_label([x1, y1, x2, y2], label, color=user_colors.get(yolo_id_to_user.get(track_id, track_id), colors(track_id, True)))

                if best_match_id == 'user_3':
                    lowest_point = get_lowest_point([x1, y1, x2, y2])
                    real_world_coords = apply_homography(lowest_point, homography_matrix)
                    logger.debug(f"Lowest point (image coords): {lowest_point}, Real-world coords: {real_world_coords}")

                    target_pan, target_tilt = PanTiltCalculator.calculate_pan_tilt(0, 0, 5, real_world_coords[0], real_world_coords[1], 0)
                    new_pan, new_tilt = LightPositionUpdater.update_light_position(current_pan, current_tilt, target_pan, target_tilt, KP)
                    
                    pan_dmx = PanTiltCalculator.pan_angle_to_dmx(new_pan, MAX_PAN)
                    tilt_dmx = PanTiltCalculator.tilt_angle_to_dmx(new_tilt, MAX_TILT)
                    
                    light_controller.set_channel_values('pan', [pan_dmx])
                    light_controller.set_channel_values('tilt', [tilt_dmx])
                    light_controller.set_channel_values('shutter', [254])
                    light_controller.set_channel_values('dimmer', [255])
                    
                    current_pan, current_tilt = new_pan, new_tilt

        frame_count += 1
        im0_annotated = annotator.result()

        if SHOW_WINDOW:
            cv2.imshow("Real-Time Detection and Tracking", im0_annotated)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            logger.info("Quitting application")
            break

    cap.release()
    cv2.destroyAllWindows()
