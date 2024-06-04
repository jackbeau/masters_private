import cv2
import logging
import os
import json
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from collections import defaultdict, deque
import uuid
import numpy as np
from reid.reid_model import extract_reid_features, load_database, match_descriptors
from light_control.controller import LightController
from light_control.pan_tilt_calculator import PanTiltCalculator, LightPositionUpdater
from utils.homography import apply_homography, seg_to_bbox, get_lowest_point, compute_homography_matrix
from video_processing import process_frame, crop_frame

# Setup logging
with open("settings.json", "r") as f:
    settings = json.load(f)

logging.basicConfig(level=getattr(logging, settings["performer_tracker"]["logging_level"].upper()))
logger = logging.getLogger(__name__)


async def start_camera_stream():
    logger.info("Starting camera stream")
    # Load YOLO model
    model = YOLO("yolov8n-seg.pt")

    # Initialize webcam
    camera_settings = settings["camera"]
    stage_zone = settings["stage_zone"]
    cap = cv2.VideoCapture(camera_settings["video_device_pos"])
    frame_count = 0
    yolo_id_to_user = {}
    track_histories = defaultdict(lambda: deque(maxlen=10))
    user_colors = {}

    # Ensure directories exist
    os.makedirs(settings["performer_tracker"]["user_folder"], exist_ok=True)
    os.makedirs(settings["performer_tracker"]["uncertain_folder"], exist_ok=True)

    database = load_database(settings["performer_tracker"]["user_folder"])
    uncertain_database = load_database(settings["performer_tracker"]["uncertain_folder"])

    # Light controller initialization
    light_controller = LightController(
        settings["performer_tracker"]["light_node_ip"],
        settings["performer_tracker"]["light_node_port"],
        settings["performer_tracker"]["light_universe_id"]
    )
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

        # # Perform cropping
        # if stage_zone["enable_crop"]:
        #     im0 = perform_crop(im0, stage_zone["crop_points"])

        # # Process the frame according to settings
        # im0 = process_frame(
        #     im0,
        #     brightness=camera_settings["brightness"],
        #     exposure=camera_settings["exposure"],
        #     contrast=camera_settings["contrast"],
        #     saturation=camera_settings["saturation"],
        #     mirror_x=camera_settings["mirror_x"],
        #     mirror_y=camera_settings["mirror_y"],
        #     clahe=camera_settings["clahe"],
        #     clahe_clip_limit=camera_settings["clahe_clip_limit"],
        #     rotation=camera_settings["rotation"],
        #     resolution=tuple(camera_settings["resolution"])
        # )

        # Perform homography
        if stage_zone["enable_homography"]:
            im0 = perform_homography(im0, stage_zone["src_points"], stage_zone["homography_width"], stage_zone["homography_height"])

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
                        user_folder = os.path.join(settings["performer_tracker"]["user_folder"], match_id)
                        os.makedirs(user_folder, exist_ok=True)

                        if frame_count % settings["performer_tracker"]["save_interval"] == 0:
                            img_name = f'{uuid.uuid4()}.jpg'
                            img_path = os.path.join(user_folder, img_name)
                            cv2.imwrite(img_path, person_image)

                        track_histories[track_id].append((match_id, score))
                    else:
                        uncertain_match_id, uncertain_score = match_descriptors(descriptors, uncertain_database, threshold=20)

                        if uncertain_match_id:
                            uncertain_user_folder = os.path.join(settings["performer_tracker"]["uncertain_folder"], uncertain_match_id)
                            os.makedirs(uncertain_user_folder, exist_ok=True)
                            img_name = f'{uuid.uuid4()}.jpg'
                            img_path = os.path.join(uncertain_user_folder, img_name)
                            cv2.imwrite(img_path, person_image)

                            track_histories[track_id].append((uncertain_match_id, uncertain_score))
                        else:
                            new_uncertain_id = f'uncertain_{len(os.listdir(settings["performer_tracker"]["uncertain_folder"]))}'
                            new_uncertain_folder = os.path.join(settings["performer_tracker"]["uncertain_folder"], new_uncertain_id)
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

                if best_match_id == settings["performer_tracker"]["tracked_user_id"]:
                    lowest_point = get_lowest_point([x1, y1, x2, y2])
                    homography_matrix = compute_homography_matrix(stage_zone["src_points"], stage_zone["dest"])
                    real_world_coords = apply_homography(lowest_point, homography_matrix)
                    logger.debug(f"Lowest point (image coords): {lowest_point}, Real-world coords: {real_world_coords}")

                    target_pan, target_tilt = PanTiltCalculator.calculate_pan_tilt(
                        *settings["performer_tracker"]["light_coords"], real_world_coords[0], real_world_coords[1], 0
                    )
                    new_pan, new_tilt = LightPositionUpdater.update_light_position(current_pan, current_tilt, target_pan, target_tilt, settings["performer_tracker"]["kp"])
                    
                    pan_dmx = PanTiltCalculator.pan_angle_to_dmx(new_pan, settings["performer_tracker"]["max_pan"])
                    tilt_dmx = PanTiltCalculator.tilt_angle_to_dmx(new_tilt, settings["performer_tracker"]["max_tilt"])
                    
                    light_controller.set_channel_values('pan', [pan_dmx])
                    light_controller.set_channel_values('tilt', [tilt_dmx])
                    light_controller.set_channel_values('shutter', [254])
                    light_controller.set_channel_values('dimmer', [255])
                    
                    current_pan, current_tilt = new_pan, new_tilt
   
        frame_count += 1
        im0_annotated = annotator.result()

        if settings["performer_tracker"]["show_window"]:
            cv2.imshow("Real-Time Detection and Tracking", im0_annotated)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            logger.info("Quitting application")
            break

    cap.release()
    cv2.destroyAllWindows()


def perform_homography(frame, src_points, width, height):
    """Perform homography transform and update the transformed image."""
    if len(src_points) == 4:
        if width == '' or height == '':  # Check if width and height are empty
            logging.error("Width and height must be set.")
            return frame
        try:
            # Get the target dimensions from the user input
            target_width = float(width)
            target_height = float(height)
        except ValueError:
            logging.error("Width and height must be valid numbers.")
            return frame
        
        src_points = sort_points_clockwise(src_points)

        src = np.array(src_points, dtype=np.float32)
        dst = np.array([
            (0, 0), 
            (target_width, 0), 
            (target_width, target_height), 
            (0, target_height)
        ], dtype=np.float32)
        h, status = cv2.findHomography(src, dst)

        try:
            original_height, original_width = frame.shape[:2]

            # Apply homography to the frame to find the transformed corner points
            corners = np.array([
                [0, 0],
                [original_width, 0],
                [original_width, original_height],
                [0, original_height]
            ], dtype=np.float32).reshape(-1, 1, 2)
            transformed_corners = cv2.perspectiveTransform(corners, h)

            # Calculate the bounding box of the transformed corners
            x_min, y_min = np.min(transformed_corners, axis=0).ravel()
            x_max, y_max = np.max(transformed_corners, axis=0).ravel()

            # Calculate the scaling factor and translation to fit the transformed image within the original size
            scale_x = original_width / (x_max - x_min)
            scale_y = original_height / (y_max - y_min)
            scale = min(scale_x, scale_y)

            # Calculate the offsets to center the image
            offset_x = (original_width - (x_max - x_min) * scale) / 2
            offset_y = (original_height - (y_max - y_min) * scale) / 2

            translation_matrix = np.array([
                [scale, 0, -x_min * scale + offset_x],
                [0, scale, -y_min * scale + offset_y],
                [0, 0, 1]
            ])

            # Combine the scaling and translation with the original homography
            combined_h = translation_matrix @ h

            # Warp the image with the combined homography
            transformed_frame = cv2.warpPerspective(frame, combined_h, (original_width, original_height), flags=cv2.INTER_LINEAR)

            # Update the transformed display with the result
            return transformed_frame
        except Exception as e:
            logging.error(f"Error performing homography: {e}")
            return frame


def perform_crop(frame, crop_points):
    """Perform cropping based on crop points and update the transformed image."""
    if len(crop_points) == 4:
        crop_points = np.array(crop_points, dtype=np.float32)
        rect = cv2.boundingRect(crop_points)
        x, y, w, h = rect
        cropped = frame[y:y+h, x:x+w].copy()

        # Create mask
        crop_points = crop_points - crop_points.min(axis=0)
        mask = np.zeros(cropped.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [crop_points.astype(np.int32)], -1, (255, 255, 255), -1, cv2.LINE_AA)

        # Bitwise AND to get the cropped region
        result = cv2.bitwise_and(cropped, cropped, mask=mask)
        return result


def sort_points_clockwise(pts):
    # Calculate the center of the quadrilateral
    center = np.mean(pts, axis=0)

    # Sort the points based on their angle relative to the center
    def angle_from_center(pt):
        return np.arctan2(pt[1] - center[1], pt[0] - center[0])

    sorted_pts = sorted(pts, key=angle_from_center)
    return sorted_pts