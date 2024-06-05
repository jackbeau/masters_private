import cv2
import logging
import os
import json
import uuid
import numpy as np
from collections import defaultdict, deque
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from reid.reid_model import extract_reid_features, load_database, match_descriptors
from light_control.controller import LightController
from light_control.pan_tilt_calculator import PanTiltCalculator
from utils.homography import apply_homography, seg_to_bbox, get_lowest_point
from video_processing import process_frame

class PerformerTracker:
    def __init__(self, settings_file="settings.json"):
        self.load_settings(settings_file)
        self.setup_logging()
        self.validate_homography_dimensions()
        self.initialize_homography()
        self.track_histories = defaultdict(lambda: deque(maxlen=10))
        self.user_colors = {}
        self.yolo_id_to_user = {}
        self.real_world_point = None

    def load_settings(self, settings_file):
        with open(settings_file, "r") as f:
            self.settings = json.load(f)

    def setup_logging(self):
        logging_level = getattr(
            logging,
            self.settings["performer_tracker"]["logging_level"].upper(),
        )
        logging.basicConfig(level=logging_level)
        self.logger = logging.getLogger(__name__)

    def validate_homography_dimensions(self):
        try:
            self.target_width = float(
                self.settings["stage_zone"]["homography_width"]
            )
            self.target_height = float(
                self.settings["stage_zone"]["homography_height"]
            )
        except ValueError:
            self.logger.error("Width and height must be valid numbers.")
            raise

    def initialize_homography(self):
        self.src_points = self.sort_points_clockwise(
            self.settings["stage_zone"]["src_points"]
        )
        self.src = np.array(self.src_points, dtype=np.float32)
        self.dst = np.array(
            [
                (0, 0),
                (self.target_width, 0),
                (self.target_width, self.target_height),
                (0, self.target_height),
            ],
            dtype=np.float32,
        )
        self.h, self.status = cv2.findHomography(self.src, self.dst)

    async def start_camera_stream(self):
        self.logger.info("Starting camera stream")
        model = YOLO("yolov8n-seg.pt")
        cap = cv2.VideoCapture(self.settings["camera"]["video_device_pos"])

        self.ensure_directories()
        database = load_database(
            self.settings["performer_tracker"]["user_folder"]
        )
        uncertain_database = load_database(
            self.settings["performer_tracker"]["uncertain_folder"]
        )

        self.light_controller = self.initialize_light_controller()

        frame_count = 0
        retry_count = 0
        max_retries = 5  # Set maximum retries

        while True:
            ret, frame = cap.read()
            if not ret:
                retry_count += 1
                self.logger.error(f"Video feed is empty, retrying... ({retry_count}/{max_retries})")
                if retry_count >= max_retries:
                    self.logger.error("Maximum retries reached. Exiting.")
                    break
                continue

            retry_count = 0  # Reset retry count on successful frame read

            frame = self.process_and_transform_frame(frame)
            annotator = Annotator(frame.copy(), line_width=2)
            results = model.track(source=frame, persist=True)

            if results[0].boxes.id is not None and results[0].masks is not None:
                self.process_detections(
                    results[0],
                    frame,
                    frame_count,
                    annotator,
                    database,
                    uncertain_database,
                )

            if self.settings["performer_tracker"]["show_window"]:
                cv2.imshow(
                    "Real-Time Detection and Tracking", annotator.result()
                )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.logger.info("Quitting application")
                break

            frame_count += 1

        cap.release()
        cv2.destroyAllWindows()

    def ensure_directories(self):
        os.makedirs(
            self.settings["performer_tracker"]["user_folder"], exist_ok=True
        )
        os.makedirs(
            self.settings["performer_tracker"]["uncertain_folder"],
            exist_ok=True,
        )

    def initialize_light_controller(self):
        light_controller = LightController(
            self.settings["performer_tracker"]["light_node_ip"],
            self.settings["performer_tracker"]["light_node_port"],
            self.settings["performer_tracker"]["light_universe_id"],
        )
        light_controller.add_channel("pan", start=18)
        light_controller.add_channel("tilt", start=20)
        light_controller.add_channel("shutter", start=2)
        light_controller.add_channel("dimmer", start=1)
        return light_controller

    def process_and_transform_frame(self, frame):
        frame = process_frame(
            frame,
            brightness=self.settings["camera"]["brightness"],
            exposure=self.settings["camera"]["exposure"],
            contrast=self.settings["camera"]["contrast"],
            saturation=self.settings["camera"]["saturation"],
            mirror_x=self.settings["camera"]["mirror_x"],
            mirror_y=self.settings["camera"]["mirror_y"],
            clahe=self.settings["camera"]["clahe"],
            clahe_clip_limit=self.settings["camera"]["clahe_clip_limit"],
            rotation=self.settings["camera"]["rotation"],
            resolution=tuple(self.settings["camera"]["resolution"]),
        )

        original_width, original_height = frame.shape[1], frame.shape[0]

        if self.settings["stage_zone"]["enable_homography"]:
            test = self.perform_homography(frame)

        # if self.settings["stage_zone"]["enable_crop"]:
        #     frame = self.perform_crop(frame)

        if self.real_world_point is not None:
            cv2.circle(test, tuple(int(x) for x in self.real_world_point), 5, (0, 255, 0), -1)

        test =  self.resize_to_original_frame(
            test, self.settings["camera"]["resolution"][0], self.settings["camera"]["resolution"][1]
        )

        cv2.imshow("Homography Transformed Frame", test)
    
        return frame

    def process_detections(
        self,
        result,
        frame,
        frame_count,
        annotator,
        database,
        uncertain_database,
    ):
        masks = result.masks.xy
        track_ids = result.boxes.id.int().cpu().tolist()
        track_masks = zip(track_ids, masks)  # Combine track IDs and masks

        for mask, track_id in zip(masks, track_ids):
            x1, y1, x2, y2 = map(int, seg_to_bbox(mask))  # Ensure coordinates are integers
            if not self.is_bbox_valid(x1, y1, x2, y2, frame):
                continue

            person_image = frame[y1:y2, x1:x2]
            if person_image.size == 0:
                continue

            descriptors = extract_reid_features(person_image)
            label = f"ID: {track_id} - Not Identified"

            if descriptors is not None and descriptors.size > 0:
                match_id, score = match_descriptors(
                    descriptors, database, threshold=15
                )

                if match_id:
                    self.save_image(
                        frame_count,
                        person_image,
                        match_id,
                        self.settings["performer_tracker"]["user_folder"],
                    )
                    self.track_histories[track_id].append((match_id, score))
                else:
                    uncertain_match_id, uncertain_score = match_descriptors(
                        descriptors, uncertain_database, threshold=20
                    )

                    if uncertain_match_id:
                        self.save_image(
                            None,
                            person_image,
                            uncertain_match_id,
                            self.settings["performer_tracker"]["uncertain_folder"],
                        )
                        self.track_histories[track_id].append(
                            (uncertain_match_id, uncertain_score)
                        )
                    else:
                        new_uncertain_id = f'uncertain_{len(os.listdir(self.settings["performer_tracker"]["uncertain_folder"]))}'
                        uncertain_database[new_uncertain_id] = [descriptors]
                        self.save_image(
                            None,
                            person_image,
                            new_uncertain_id,
                            self.settings["performer_tracker"]["uncertain_folder"],
                        )
                        self.track_histories[track_id].append((new_uncertain_id, 0))

            if len(self.track_histories[track_id]) > 0:
                label = self.update_track_histories(track_id)

            annotator.box_label(
                [x1, y1, x2, y2], label,
                color=self.user_colors.get(self.yolo_id_to_user.get(track_id, track_id), colors(track_id, True))
            )

        if (
            self.settings["performer_tracker"]["tracked_user_id"]
            in self.yolo_id_to_user.values()
        ):
            self.update_light_position(track_masks, frame, annotator)
 

    def is_bbox_valid(self, x1, y1, x2, y2, frame):
        return (
            x1 >= 0 and y1 >= 0 and x2 < frame.shape[1] and y2 < frame.shape[0]
        )

    def handle_descriptors(
        self,
        descriptors,
        frame_count,
        person_image,
        track_id,
        database,
        uncertain_database,
    ):
        if descriptors is not None and descriptors.size > 0:
            match_id, score = match_descriptors(
                descriptors, database, threshold=15
            )

            if match_id:
                self.save_image(
                    frame_count,
                    person_image,
                    match_id,
                    self.settings["performer_tracker"]["user_folder"],
                )
                self.track_histories[track_id].append((match_id, score))
            else:
                self.handle_uncertain_matches(
                    descriptors, person_image, track_id, uncertain_database
                )

        if len(self.track_histories[track_id]) > 0:
            self.update_track_histories(track_id)

    def handle_uncertain_matches(
        self, descriptors, person_image, track_id, uncertain_database
    ):
        uncertain_match_id, uncertain_score = match_descriptors(
            descriptors, uncertain_database, threshold=20
        )

        if uncertain_match_id:
            self.save_image(
                None,
                person_image,
                uncertain_match_id,
                self.settings["performer_tracker"]["uncertain_folder"],
            )
            self.track_histories[track_id].append(
                (uncertain_match_id, uncertain_score)
            )
        else:
            new_uncertain_id = f'uncertain_{len(os.listdir(self.settings["performer_tracker"]["uncertain_folder"]))}'
            uncertain_database[new_uncertain_id] = [descriptors]
            self.save_image(
                None,
                person_image,
                new_uncertain_id,
                self.settings["performer_tracker"]["uncertain_folder"],
            )
            self.track_histories[track_id].append((new_uncertain_id, 0))

    def save_image(self, frame_count, person_image, match_id, folder):
        if (
            frame_count is None
            or frame_count
            % self.settings["performer_tracker"]["save_interval"]
            == 0
        ):
            user_folder = os.path.join(folder, match_id)
            os.makedirs(user_folder, exist_ok=True)
            img_name = f"{uuid.uuid4()}.jpg"
            img_path = os.path.join(user_folder, img_name)
            cv2.imwrite(img_path, person_image)

    def update_track_histories(self, track_id):
        id_counts = defaultdict(int)
        for id, score in self.track_histories[track_id]:
            id_counts[id] += 1
        best_match_id = max(id_counts, key=id_counts.get)
        match_percentage = (
            id_counts[best_match_id] / len(self.track_histories[track_id])
        ) * 100
        best_score = min(
            score
            for id, score in self.track_histories[track_id]
            if id == best_match_id
        )
        label = f"ID: {track_id} - {best_match_id} ({match_percentage:.2f}%) Score: {best_score:.2f}"
        self.yolo_id_to_user[track_id] = best_match_id
        self.user_colors[best_match_id] = colors(len(self.user_colors), True)
        return label

    def update_light_position(self, track_masks, frame, annotator):
        for track_id, mask in track_masks:
            if (
                self.yolo_id_to_user.get(track_id)
                == self.settings["performer_tracker"]["tracked_user_id"]
            ):
                x1, y1, x2, y2 = map(int, seg_to_bbox(mask))  # Ensure coordinates are integers
                lowest_point = np.array([[get_lowest_point([x1, y1, x2, y2])]], dtype=np.float32)  
                real_world_coords = cv2.perspectiveTransform(lowest_point, self.h)[0][0]  # Adjust indexing

                self.logger.debug(
                    f"Lowest point (image coords): {lowest_point}, Real-world coords: {real_world_coords}"
                )

                target_pan, target_tilt = PanTiltCalculator.calculate_pan_tilt(
                    *self.settings["performer_tracker"]["light_coords"],
                    real_world_coords[0],
                    real_world_coords[1],
                    0,
                )

                # Martin Mac 700 Profile

                pan_dmx = PanTiltCalculator.pan_angle_to_dmx(
                    target_pan, self.settings["performer_tracker"]["max_pan"]
                )
                tilt_dmx = PanTiltCalculator.tilt_angle_to_dmx(
                    target_tilt, self.settings["performer_tracker"]["max_tilt"]
                )

                self.light_controller.set_channel_values("pan", [pan_dmx])
                self.light_controller.set_channel_values("tilt", [tilt_dmx])
                self.light_controller.set_channel_values("shutter", [254])
                self.light_controller.set_channel_values("dimmer", [255])

                self.real_world_point = real_world_coords


    def perform_homography(self, frame):
        if len(self.src_points) == 4:
            transformed_frame = cv2.warpPerspective(
                frame,
                self.h,
                (int(self.target_width), int(self.target_height)),
            )
            return transformed_frame
        return frame

    def perform_crop(self, frame):
        crop_points = np.array(
            self.settings["stage_zone"]["crop_points"], dtype=np.float32
        )

        if (
            self.settings["stage_zone"]["enable_homography"]
            and len(crop_points) == 4
        ):
            crop_points = cv2.perspectiveTransform(
                np.array([crop_points], dtype=np.float32), self.h
            )[0]

        crop_points[:, 0] = np.clip(crop_points[:, 0], 0, frame.shape[1] - 1)
        crop_points[:, 1] = np.clip(crop_points[:, 1], 0, frame.shape[0] - 1)

        rect = cv2.boundingRect(crop_points)
        x, y, w, h = rect
        cropped = frame[y : y + h, x : x + w].copy()

        crop_points -= crop_points.min(axis=0)
        mask = np.zeros(cropped.shape[:2], dtype=np.uint8)
        cv2.drawContours(
            mask,
            [crop_points.astype(np.int32)],
            -1,
            (255, 255, 255),
            -1,
            cv2.LINE_AA,
        )

        result = cv2.bitwise_and(cropped, cropped, mask=mask)
        return result

    @staticmethod
    def sort_points_clockwise(pts):
        center = np.mean(pts, axis=0)

        def angle_from_center(pt):
            return np.arctan2(pt[1] - center[1], pt[0] - center[0])

        sorted_pts = sorted(pts, key=angle_from_center)
        return sorted_pts

    @staticmethod
    def resize_to_original_frame(frame, original_width, original_height):
        return cv2.resize(frame, (original_width, original_height))


# Instantiate and run the performer tracker
if __name__ == "__main__":
    tracker = PerformerTracker()
    import asyncio
    asyncio.run(tracker.start_camera_stream())
