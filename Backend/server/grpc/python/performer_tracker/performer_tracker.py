"""
Performer Tracking System

This module implements a performer tracking system using YOLO for detection
and ReID for re-identification.
The system processes frames from a camera, performs homography transformations,
and controls lighting based on performer locations.

Author: Jack Beaumont
Date: 06/06/2024
"""

import cv2
import logging
import os
import sys
import uuid
import numpy as np
from collections import defaultdict, deque
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from reid.reid_model import PersonReID
from light_control.controller import LightController
from light_control.pan_tilt_calculator import (
    PanTiltCalculator,
)
from utils.homography import seg_to_bbox, get_center_point
from video_processing import process_frame
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))


class PerformerTracker:
    def __init__(self, settings, status_queue=None):
        """
        Initializes the PerformerTracker with the given settings and optional
        status queue.

        :param settings: Configuration settings for the performer tracker.
        :param status_queue: Queue to communicate status messages (optional).
        """
        self.settings = settings
        self.status_queue = status_queue
        self.setup_logging()
        self.validate_homography_dimensions()
        self.initialize_homography()
        self.track_histories = defaultdict(lambda: deque(maxlen=10))
        self.user_colors = {}
        self.yolo_id_to_user = {}
        self.real_world_point = None
        self.light_controller = None
        self.stop = False
        self.reid_model = PersonReID()

    def setup_logging(self):
        """
        Set up logging configuration based on settings.
        """
        logging_level = getattr(
            logging,
            self.settings["performer_tracker"]["logging_level"].upper(),
        )
        logging.basicConfig(level=logging_level)
        self.logger = logging.getLogger(__name__)

    def validate_homography_dimensions(self):
        """
        Validate and set homography dimensions from settings.
        """
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
        """
        Initialize the homography transformation using source points from
        settings.
        """
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
        """
        Start the camera stream for performer tracking.
        """
        self.logger.info("Starting camera stream")
        model = YOLO("yolov8n-seg.pt")
        cap = cv2.VideoCapture(self.settings["camera"]["video_device_pos"])

        self.ensure_directories()
        database = self.reid_model.load_database(
            self.settings["performer_tracker"]["user_folder"]
        )
        uncertain_database = self.reid_model.load_database(
            self.settings["performer_tracker"]["uncertain_folder"]
        )

        frame_count = 0
        retry_count = 0
        max_retries = 5

        while not self.stop:
            ret, frame = cap.read()
            if not ret:
                retry_count += 1
                self.logger.error(
                    "Video feed is empty, retrying... "
                    f"({retry_count}/{max_retries})"
                )
                if retry_count >= max_retries:
                    self.logger.error("Maximum retries reached. Exiting.")
                    break
                continue

            retry_count = 0

            frame = self.process_and_transform_frame(frame)
            annotator = Annotator(frame.copy(), line_width=2)
            results = model.track(source=frame, persist=True)

            if (
                results[0].boxes.id is not None
                and results[0].masks is not None
            ):
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
                    "Real-Time Detection and Tracking", annotator.result
                )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.logger.info("Quitting application")
                break

            frame_count += 1

            await asyncio.sleep(0.01)

        cap.release()
        cv2.destroyAllWindows()

        if not self.stop:
            self.logger.error(
                "Performer tracker loop exited unexpectedly. "
                "Stopping the light controller."
            )
            self.stop()

    def ensure_directories(self):
        """
        Ensure that the necessary directories for storing images exist.
        """
        os.makedirs(
            self.settings["performer_tracker"]["user_folder"], exist_ok=True
        )
        os.makedirs(
            self.settings["performer_tracker"]["uncertain_folder"],
            exist_ok=True,
        )

    def process_and_transform_frame(self, frame):
        """
        Process and transform the input frame based on settings.

        :param frame: Input video frame.
        :return: Processed and transformed frame.
        """
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

        if self.settings["stage_zone"]["enable_homography"]:
            test = self.perform_homography(frame)

            if self.real_world_point is not None:
                cv2.circle(
                    test,
                    tuple(int(x) for x in self.real_world_point),
                    20,
                    (0, 0, 255),
                    -1,
                )

            test = self.resize_to_original_frame(
                test,
                self.settings["camera"]["resolution"][0],
                self.settings["camera"]["resolution"][1],
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
        """
        Process detections from the YOLO model and update tracking information.

        :param result: Detection results from YOLO model.
        :param frame: Current video frame.
        :param frame_count: Current frame count.
        :param annotator: Annotator object for drawing on the frame.
        :param database: Database of known persons.
        :param uncertain_database: Database of uncertain identities.
        """
        masks = result.masks.xy
        track_ids = result.boxes.id.int().cpu().tolist()
        track_masks = zip(track_ids, masks)

        for mask, track_id in track_masks:
            x1, y1, x2, y2 = map(int, seg_to_bbox(mask))
            if not self.is_bbox_valid(x1, y1, x2, y2, frame):
                continue

            person_image = frame[y1:y2, x1:x2]
            if person_image.size == 0:
                continue

            descriptors = self.reid_model.extract_reid_features(person_image)
            label = f"ID: {track_id} - Not Identified"

            if descriptors is not None and descriptors.size > 0:
                match_id, score = self.reid_model.match_descriptors(
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
                    uncertain_match_id, uncertain_score = (
                        self.reid_model.match_descriptors(
                            descriptors, uncertain_database, threshold=20
                        )
                    )

                    if uncertain_match_id:
                        self.save_image(
                            None,
                            person_image,
                            uncertain_match_id,
                            self.settings["performer_tracker"][
                                "uncertain_folder"
                            ],
                        )
                        self.track_histories[track_id].append(
                            (uncertain_match_id, uncertain_score)
                        )
                    else:
                        performer_track = self.settings["performer_tracker"]
                        uncertain_folder = performer_track["uncertain_folder"]
                        new_uncertain_id = f'uncertain_{
                            len(os.listdir(uncertain_folder))
                        }'
                        uncertain_database[new_uncertain_id] = [descriptors]
                        self.save_image(
                            None,
                            person_image,
                            new_uncertain_id,
                            self.settings["performer_tracker"][
                                "uncertain_folder"
                            ],
                        )
                        self.track_histories[track_id].append(
                            (new_uncertain_id, 0)
                        )

            if len(self.track_histories[track_id]) > 0:
                label = self.update_track_histories(track_id)

            annotator.box_label(
                [x1, y1, x2, y2],
                label,
                color=self.user_colors.get(
                    self.yolo_id_to_user.get(track_id, track_id),
                    colors(track_id, True),
                ),
            )

        if (
            self.settings["performer_tracker"]["tracked_user_id"]
            in self.yolo_id_to_user.values()
        ):
            self.update_light_position(track_masks, frame, annotator)

    def is_bbox_valid(self, x1, y1, x2, y2, frame):
        """
        Validate if the bounding box coordinates are within frame dimensions.

        :param x1: Top-left x-coordinate of the bounding box.
        :param y1: Top-left y-coordinate of the bounding box.
        :param x2: Bottom-right x-coordinate of the bounding box.
        :param y2: Bottom-right y-coordinate of the bounding box.
        :param frame: Current video frame.
        :return: Boolean indicating if the bounding box is valid.
        """
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
        """
        Handle descriptors extracted from a person's image and update tracking
        information.

        :param descriptors: ReID descriptors of the person.
        :param frame_count: Current frame count.
        :param person_image: Cropped image of the person.
        :param track_id: Track ID assigned by YOLO.
        :param database: Database of known persons.
        :param uncertain_database: Database of uncertain identities.
        """
        if descriptors is not None and descriptors.size > 0:
            match_id, score = self.reid_model.match_descriptors(
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
        """
        Handle uncertain matches by updating the uncertain database.

        :param descriptors: ReID descriptors of the person.
        :param person_image: Cropped image of the person.
        :param track_id: Track ID assigned by YOLO.
        :param uncertain_database: Database of uncertain identities.
        """
        uncertain_match_id, uncertain_score = (
            self.reid_model.match_descriptors(
                descriptors, uncertain_database, threshold=20
            )
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
            performer_track = self.settings["performer_tracker"]
            uncertain_folder = performer_track["uncertain_folder"]
            new_uncertain_id = f'uncertain_{
                len(os.listdir(uncertain_folder))
            }'
            uncertain_database[new_uncertain_id] = [descriptors]
            self.save_image(
                None,
                person_image,
                new_uncertain_id,
                self.settings["performer_tracker"]["uncertain_folder"],
            )
            self.track_histories[track_id].append((new_uncertain_id, 0))

    def save_image(self, frame_count, person_image, match_id, folder):
        """
        Save an image of the person to the specified folder.

        :param frame_count: Current frame count.
        :param person_image: Cropped image of the person.
        :param match_id: Matched ID of the person.
        :param folder: Folder to save the image in.
        """
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
        """
        Update track histories and determine the best match ID for the given
        track ID.

        :param track_id: Track ID assigned by YOLO.
        :return: Label for the bounding box with the best match ID.
        """
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
        label = (
            f"ID: {track_id} - {best_match_id} ({match_percentage:.2f}%) "
            f"Score: {best_score:.2f}"
        )
        self.yolo_id_to_user[track_id] = best_match_id
        self.user_colors[best_match_id] = colors(len(self.user_colors), True)
        return label

    def is_point_in_polygon(self, point, polygon):
        """
        Check if a point is inside a polygon.

        :param point: Point to check.
        :param polygon: Polygon represented as a list of points.
        :return: Boolean indicating if the point is inside the polygon.
        """
        result = cv2.pointPolygonTest(
            np.array(polygon, dtype=np.float32), point, False
        )
        return result >= 0

    def closest_point_on_segment(self, pt, v, w):
        """
        Find the closest point on a line segment to a given point.

        :param pt: Point to find the closest point to.
        :param v: Start point of the line segment.
        :param w: End point of the line segment.
        :return: Closest point on the line segment to pt.
        """
        l2 = np.sum((v - w) ** 2)
        if l2 == 0:
            return v
        t = np.dot(pt - v, w - v) / l2
        t = max(0, min(1, t))
        projection = v + t * (w - v)
        return projection

    def closest_point_on_polygon(self, point, polygon):
        """
        Find the closest point on a polygon to a given point.

        :param point: Point to find the closest point to.
        :param polygon: Polygon represented as a list of points.
        :return: Closest point on the polygon to the given point.
        """
        min_dist = float("inf")
        closest_point = None
        for i in range(len(polygon)):
            line_start = np.array(polygon[i], dtype=np.float32)
            line_end = np.array(
                polygon[(i + 1) % len(polygon)], dtype=np.float32
            )
            proj_point = self.closest_point_on_segment(
                point, line_start, line_end
            )
            distance = np.linalg.norm(proj_point - point)
            if distance < min_dist:
                min_dist = distance
                closest_point = proj_point
        return closest_point

    def update_light_position(self, track_masks, frame, annotator):
        """
        Update the light position based on the tracked user's location.

        :param track_masks: List of tracked IDs and their corresponding masks.
        :param frame: Current video frame.
        :param annotator: Annotator object for drawing on the frame.
        """
        for track_id, mask in track_masks:
            if (
                self.yolo_id_to_user.get(track_id)
                == self.settings["performer_tracker"]["tracked_user_id"]
            ):
                x1, y1, x2, y2 = map(int, seg_to_bbox(mask))
                center_point = np.array(
                    [[get_center_point([x1, y1, x2, y2])]], dtype=np.float32
                )

                real_world_coords = cv2.perspectiveTransform(
                    center_point, self.h
                )[0][0]
                real_world_coords = np.round(real_world_coords, decimals=0)

                self.logger.debug(
                    f"Lowest point (image coords): {center_point}, "
                    f"Real-world coords: {real_world_coords}"
                )

                self.real_world_point = real_world_coords

                cv2.circle(
                    frame,
                    (int(center_point[0][0][0]), int(center_point[0][0][1])),
                    5,
                    (0, 255, 0),
                    -1,
                )
                annotator.result = frame

    def perform_homography(self, frame):
        """
        Perform homography transformation on the input frame.

        :param frame: Input video frame.
        :return: Transformed frame.
        """
        if len(self.src_points) == 4:
            transformed_frame = cv2.warpPerspective(
                frame,
                self.h,
                (int(self.target_width), int(self.target_height)),
            )
            return transformed_frame
        return frame

    def perform_crop(self, frame):
        """
        Perform cropping on the input frame based on settings.

        :param frame: Input video frame.
        :return: Cropped frame.
        """
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
        cropped = frame[y: y + h, x: x + w].copy()

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
        """
        Sort points in clockwise order.

        :param pts: List of points to sort.
        :return: Sorted list of points.
        """
        center = np.mean(pts, axis=0)

        def angle_from_center(pt):
            return np.arctan2(pt[1] - center[1], pt[0] - center[0])

        sorted_pts = sorted(pts, key=angle_from_center)
        return sorted_pts

    @staticmethod
    def resize_to_original_frame(frame, original_width, original_height):
        """
        Resize the frame to its original dimensions.

        :param frame: Input video frame.
        :param original_width: Original width of the frame.
        :param original_height: Original height of the frame.
        :return: Resized frame.
        """
        return cv2.resize(frame, (original_width, original_height))

    async def light_control_loop(self):
        """
        Light control loop to update the light position based on performer
        location.
        """
        x0, y0, z0 = self.settings["performer_tracker"]["light_coords"]
        max_pan = self.settings["performer_tracker"]["max_pan"]
        max_tilt = self.settings["performer_tracker"]["max_tilt"]

        self.logger.info("Starting light control loop")

        self.light_controller = LightController(
            self.settings["performer_tracker"]["light_node_ip"],
            self.settings["performer_tracker"]["light_node_port"],
            self.settings["performer_tracker"]["light_universe_id"],
        )
        self.light_controller.add_channel("pan", start=18)
        self.light_controller.add_channel("tilt", start=20)
        self.light_controller.add_channel("shutter", start=1)
        self.light_controller.add_channel("dimmer", start=2)

        try:
            while not self.stop:
                self.logger.debug("Light control loop running")
                if self.real_world_point is not None:
                    self.logger.debug("Updating DMX")
                    xt, yt, zt = (
                        self.real_world_point[0],
                        int(self.settings["stage_zone"]["homography_height"])
                        - self.real_world_point[1],
                        0,
                    )
                    target_pan, target_tilt = (
                        PanTiltCalculator.calculate_pan_tilt(
                            x0, y0, z0, xt, yt, zt
                        )
                    )

                    pan_dmx = PanTiltCalculator.pan_angle_to_dmx(
                        target_pan, max_pan
                    )
                    tilt_dmx = PanTiltCalculator.tilt_angle_to_dmx(
                        target_tilt, max_tilt
                    )

                    self.light_controller.set_channel_values("pan", [pan_dmx])
                    self.light_controller.set_channel_values(
                        "tilt", [tilt_dmx]
                    )
                    self.light_controller.set_channel_values("shutter", [25])
                    self.light_controller.set_channel_values("dimmer", [255])

                await asyncio.sleep(0.1)
        except asyncio.CancelledError as e:
            self.logger.info("Light control loop cancelled")
            self.logger.error(e)
            if not self.stop:
                self.logger.error(
                    "Light control loop cancelled unexpectedly, stopping the "
                    "performer tracker."
                )
                self.stop()

    def start(self):
        """
        Start the performer tracking system.
        """
        self.stop = False
        if self.status_queue:
            self.status_queue.put("Started")
        asyncio.run(self.main())

    def stop(self):
        """
        Stop the performer tracking system.
        """
        self.stop = True
        if self.status_queue:
            self.status_queue.put("Stopped")

    async def main(self):
        """
        Main coroutine to run the light control loop and camera stream
        concurrently.
        """
        await asyncio.gather(
            self.light_control_loop(), self.start_camera_stream()
        )
