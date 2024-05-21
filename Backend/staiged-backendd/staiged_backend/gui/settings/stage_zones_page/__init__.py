from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import multiprocessing
import asyncio
import cv2
import numpy as np
from gui.styles import text, colours
from utils.standard_resolutions import standard_resolutions
import utils.video_utils
import logging
from gui.settings.settings_manager import CameraSettingsManager, StageZoneSettingsManager
from multiprocessing import Manager
from gui.settings.stage_zones_page.video_processing import video_loop
from utils import SettingsManager

class FloatEntry(ttk.Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vcmd = (self.register(self.validate),'%P')
        self.config(validate="all", validatecommand=vcmd)

    def validate(self, text):
        if (
            all(char in "0123456789.-" for char in text) and  # all characters are valid
            "-" not in text[1:] and # "-" is the first character or not present
            text.count(".") <= 1): # only 0 or 1 periods
                return True
        else:
            return False
        
class StageZonesPage(tk.Frame):
    NAME = "Stage Zones"

    def __init__(self, parent, settings_file="settings.json", *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        
        # Initialize attributes
        self.resizing = False
        self.stop_event = multiprocessing.Event()
        self.frame_queue = multiprocessing.Queue(maxsize=1)
        self.hist_queue = multiprocessing.Queue(maxsize=1)
        self.manager = Manager()
        self.settings = self.manager.dict()
        
        # Initialize settings managers
        self.camera_settings_manager = CameraSettingsManager(settings_file)
        self.stage_zone_settings_manager = StageZoneSettingsManager(settings_file)
        self.load_settings()
        
        # Get video device info and their maximum resolutions
        self.get_video_device_info()
        
        # Start video capture and processing
        self.start_processes()
        
        # Start asynchronous tasks for updating frame and plot
        self.start_async_tasks()
        
        # Initialize points for homography and cropping
        self.dragging_point = None  # To track which point is being dragged
        self.current_frame = None  # Initialize current_frame

        # Render the UI
        self.render()

    def get_video_device_info(self):
        """Get information about the video device."""
        self.video_devices = utils.video_utils.get_video_devices()
        try:
            # Using a generator expression with next to find the device
            device = next((device for device in self.video_devices if device["uniqueID"] == self.video_device_id), None)

            if device:
                self.video_device_name = device["localizedName"]
                self.video_device_position = device["position"]
                self.update_settings_queue()
                return
            # No match found
            self.video_device_position = None
            self.video_device_name = None
            self.update_settings_queue()
            
        except ValueError:
            self.video_device_position = None
            self.video_device_name = None
            print(f"Device with ID {self.video_device_id} not found.")

    def load_settings(self):
        """Load settings from the settings managers."""
        # Load camera settings
        camera_settings = self.camera_settings_manager.get_camera_settings()
        self.video_device_id = camera_settings.get('video_device_id', 0)
        self.rotation = camera_settings.get('rotation', 0)
        self.res = camera_settings.get('resolution', ())
        self.mirror_x = tk.IntVar(value=camera_settings.get('mirror_x', 0))
        self.mirror_y = tk.IntVar(value=camera_settings.get('mirror_y', 0))
        self.hist_equalisation = tk.IntVar(value=camera_settings.get('hist_equalisation', 0))
        self.brightness = tk.DoubleVar(value=camera_settings.get('brightness', 50))
        self.exposure = tk.DoubleVar(value=camera_settings.get('exposure', 50))
        self.contrast = tk.DoubleVar(value=camera_settings.get('contrast', 50))
        self.saturation = tk.DoubleVar(value=camera_settings.get('saturation', 50))

        # Load stage zone settings
        stage_zone_settings = self.stage_zone_settings_manager.get_stage_zone_settings()
        self.src_points = stage_zone_settings.get('src_points', [])
        self.crop_points = stage_zone_settings.get('crop_points', [])
        self.enable_crop = tk.IntVar(value=stage_zone_settings.get('enable_crop', 0))
        self.enable_homography = tk.IntVar(value=stage_zone_settings.get('enable_homography', 0))
        self.homography_width = tk.StringVar(value=stage_zone_settings.get('homography_width', ''))
        self.homography_height = tk.StringVar(value=stage_zone_settings.get('homography_height', ''))

        self.homography_width.trace_add("write", self.save_settings)
        self.homography_height.trace_add("write", self.save_settings)


    def save_settings(self, *args):
        """Save current settings to the settings managers."""
        if self.crop_points == []:
            self.reset_crop_points()
        # Save camera settings
        camera_settings = {
            'video_device_id': self.video_device_id,
            'video_device_pos': self.video_device_position,
            'resolution': self.res,
            'rotation': self.rotation,
            'mirror_x': self.mirror_x.get(),
            'mirror_y': self.mirror_y.get(),
            'hist_equalisation': self.hist_equalisation.get(),
            'brightness': self.brightness.get(),
            'exposure': self.exposure.get(),
            'contrast': self.contrast.get(),
            'saturation': self.saturation.get(),
        }
        self.camera_settings_manager.save_camera_settings(camera_settings)
        self.update_settings_queue()

        # Save stage zone settings
        stage_zone_settings = {
            'src_points': self.src_points,
            'crop_points': self.crop_points,
            'enable_crop': self.enable_crop.get(),
            'enable_homography': self.enable_homography.get(),
            'homography_width': self.homography_width.get(),
            'homography_height': self.homography_height.get(),
        }
        self.stage_zone_settings_manager.save_stage_zone_settings(stage_zone_settings)

    def update_settings_queue(self):
        """Update the settings queue with current settings."""
        self.settings.update({
            'video_device_id': self.video_device_id,
            'video_device_pos': self.video_device_position,
            'resolution': self.res,
            'rotation': self.rotation,
            'mirror_x': self.mirror_x.get(),
            'mirror_y': self.mirror_y.get(),
            'hist_equalisation': self.hist_equalisation.get(),
            'brightness': self.brightness.get(),
            'exposure': self.exposure.get(),
            'contrast': self.contrast.get(),
            'saturation': self.saturation.get()
        })

    def close(self):
        """Handle closing of the camera page."""
        self.stop_event.set()
        self.video_process.terminate()
        self.video_process.join()  # This should now not hang

    def start_processes(self):
        """Start video and plot processing in separate processes."""
        self.stop_event.clear()
        self.video_process = multiprocessing.Process(
            target=video_loop,
            args=(self.frame_queue, self.stop_event, self.settings)
        )
        self.video_process.start()

    def start_async_tasks(self):
        """Start asynchronous tasks for updating frame and plot."""
        asyncio.create_task(self.update_frame())
        
    def reset_homography(self):
        """Reset homography points."""
        self.src_points = []
        self.update_frame_display(self.current_frame, draw_points=True)
        self.save_settings()

    def reset_crop(self):
        """Reset crop points to default."""
        self.reset_crop_points()
        self.update_frame_display(self.current_frame, draw_points=True)
        self.save_settings()

    def reset_crop_points(self):
        """Initialize crop points to default state."""
        if self.current_frame is not None:
            h, w = self.current_frame.shape[:2]
            margin = 20
            self.crop_points = [(margin, margin), (w - margin, margin), (w - margin, h - margin), (margin, h - margin)]
        else:
            self.crop_points = [(20, 20), (480, 20), (480, 320), (20, 320)]  # Default values for a 500x340 frame

    def render(self):
        """
        Render the GUI
        """
        # Description and instructions
        lbl_description = text(self, text="Use this interface to enable cropping and homography transformation. Drag the green points to set the source quadrilateral and the red points to set the destination quadrilateral. This only works for a plane of constant height.", style="PageText")
        lbl_description.pack(fill="x", pady=(0, 4), anchor="w")

        # Settings frame
        frm_settings = tk.Frame(self, background=colours.off_black_80)
        frm_settings.pack(fill="x", pady=(0, 4))

        # Enable crop checkbox
        chk_crop = ttk.Checkbutton(
            frm_settings, text="Enable Crop",
            style="Label.TCheckbutton",
            variable=self.enable_crop,
            command=self.save_settings
        )
        chk_crop.pack(side="left", padx=(0, 8))

        # Enable homography transform checkbox
        chk_homography = ttk.Checkbutton(
            frm_settings, text="Enable Homography Transform",
            style="Label.TCheckbutton",
            variable=self.enable_homography,
            command=self.save_settings
        )
        chk_homography.pack(side="left", padx=(0, 8))

        # Set homography points button
        btn_set_homography = ttk.Button(
            frm_settings,
            text="Set Homography Points",
            command=self.set_homography_points,
            style="Label.TButton"
        )
        btn_set_homography.pack(side="left", padx=(0, 8))

        # Reset homography points button
        btn_rst_homography = ttk.Button(
            frm_settings,
            text="Reset Homography Points",
            command=self.reset_homography,
            style="Label.TButton"
        )
        btn_rst_homography.pack(side="left", padx=(0, 8))

        # Reset crop points button
        btn_rst_crop = ttk.Button(
            frm_settings,
            text="Reset Crop Points",
            command=self.reset_crop,
            style="Label.TButton"
        )
        btn_rst_crop.pack(side="left", padx=(0, 8))

        # Frame for width and height inputs
        frm_size_inputs = tk.Frame(self, background=colours.off_black_80)
        frm_size_inputs.pack(fill="x", pady=(0, 8))

        lbl_width = text(frm_size_inputs, text="Width (m)", style="PageText")
        lbl_width.pack(side="left", padx=(0, 4))
        self.width_entry = FloatEntry(frm_size_inputs, textvariable=self.homography_width)
        self.width_entry.pack(side="left", padx=(0, 8))

        lbl_height = text(frm_size_inputs, text="Height (m)", style="PageText")
        lbl_height.pack(side="left", padx=(0, 4))
        self.height_entry = FloatEntry(frm_size_inputs, textvariable=self.homography_height)
        self.height_entry.pack(side="left", padx=(0, 8))

        # Frame for video feed and transformed result side by side
        frm_video_and_result = tk.Frame(self, background=colours.off_black_80)
        frm_video_and_result.pack(fill="both", expand=True, pady=(0, 0))

        # Frame for video feed
        frm_video = tk.Frame(frm_video_and_result, background=colours.off_black_80)
        frm_video.pack(side="left", expand=True, fill="both", padx=(0, 8))

        # Video input title
        lbl_vid_input = text(frm_video, text="Camera Feed", style="PageHeading2")
        lbl_vid_input.pack(fill="x", pady=(0, 4))

        # Live feed frame
        self.frm_video = ttk.Label(frm_video, image=None, anchor="center", justify="center", text="Loading video...", background="black", foreground="white")
        self.frm_video.pack(expand=False)  # Change expand to False

        # Frame for homography result
        frm_bottom = tk.Frame(frm_video_and_result, background=colours.off_black_80)
        frm_bottom.pack(side="left", expand=True, fill="both", padx=(0, 0)) # No padding last item

        # Homography result title
        lbl_homography_result = text(frm_bottom, text="Homography Transform Result", style="PageHeading2")
        lbl_homography_result.pack(fill="x", pady=(0, 4))

        # Transformed feed frame
        self.frm_transformed = ttk.Label(frm_bottom, image=None, anchor="center", justify="center", text="Loading transform...", background="black", foreground="white")
        self.frm_transformed.pack(expand=False)  # Change expand to False

        # Bind mouse events to select and drag points for homography and crop
        self.frm_video.bind("<Button-1>", self.on_mouse_click)
        self.frm_video.bind("<B1-Motion>", self.on_mouse_drag)
        self.frm_video.bind("<ButtonRelease-1>", self.on_mouse_release)

    def set_homography_points(self):
        """Set homography points."""
        self.enable_homography.set(True)

    def on_mouse_click(self, event):
        """Handle mouse click to select or start dragging points for homography and crop."""
        widget = event.widget
        if widget == self.frm_video:
            widget_width = widget.winfo_width()
            widget_height = widget.winfo_height()
            image_width, image_height = self.current_frame.shape[1], self.current_frame.shape[0]

            # Calculate the scaling factors and offset
            scale_x = image_width / widget_width
            scale_y = image_height / widget_height
            offset_x = (widget_width - image_width / scale_x) / 2
            offset_y = (widget_height - image_height / scale_y) / 2

            point = (int((event.x - offset_x) * scale_x), int((event.y - offset_y) * scale_y))

            if self.enable_homography.get():
                if len(self.src_points) < 4:
                    self.src_points.append(point)
                    self.save_settings()
                else:
                    # Check if the click is close to an existing point to start dragging
                    for i, src_point in enumerate(self.src_points):
                        if self.is_close(point, src_point):
                            self.dragging_point = i
                            break
            if self.enable_crop.get():
                for i, crop_point in enumerate(self.crop_points):
                    if self.is_close(point, crop_point):
                        self.dragging_point = i + 4  # Offset to differentiate from homography points
                        break
            self.update_frame_display(self.current_frame, draw_points=True)

    def on_mouse_drag(self, event):
        """Handle mouse drag to move points for homography and crop."""
        widget = event.widget
        if self.dragging_point is not None and widget == self.frm_video:
            widget_width = widget.winfo_width()
            widget_height = widget.winfo_height()
            image_width, image_height = self.current_frame.shape[1], self.current_frame.shape[0]

            # Calculate the scaling factors and offset
            scale_x = image_width / widget_width
            scale_y = image_height / widget_height
            offset_x = (widget_width - image_width / scale_x) / 2
            offset_y = (widget_height - image_height / scale_y) / 2

            point = (int((event.x - offset_x) * scale_x), int((event.y - offset_y) * scale_y))

            # Clamp the point within the frame boundaries
            point = (
                max(0, min(point[0], image_width - 1)),
                max(0, min(point[1], image_height - 1))
            )

            if self.dragging_point < 4:
                self.src_points[self.dragging_point] = point
               
            else:
                self.crop_points[self.dragging_point - 4] = point
            self.update_frame_display(self.current_frame, draw_points=True)
            self.save_settings

    def update_frame_display(self, frame, draw_points=False):
        """Update the displayed frame with optional points drawing."""
        frame_copy = frame.copy()  # Copy the frame to avoid drawing on the original
        if draw_points:
            # Draw homography points and lines
            for i, point in enumerate(self.src_points):
                cv2.circle(frame_copy, point, 5, (0, 255, 0), -1)
                if i > 0:
                    cv2.line(frame_copy, self.src_points[i - 1], point, (0, 255, 0), 2)
            if len(self.src_points) == 4:
                cv2.line(frame_copy, self.src_points[0], self.src_points[3], (0, 255, 0), 2)

            # Draw crop points and lines if cropping is enabled
            if self.enable_crop.get():
                if len(self.crop_points) == 4:
                    for i, point in enumerate(self.crop_points):
                        cv2.circle(frame_copy, point, 5, (255, 0, 0), -1)
                        if i > 0:
                            cv2.line(frame_copy, self.crop_points[i - 1], point, (255, 0, 0), 2)
                    cv2.line(frame_copy, self.crop_points[0], self.crop_points[3], (255, 0, 0), 2)

        # Resize the image to fit the frame without black borders
        image = Image.fromarray(frame_copy)
        image = ImageTk.PhotoImage(image)
        self.frm_video.configure(image=image)
        self.frm_video.image = image
        self.frm_video.pack_propagate(False)
        self.frm_video.config(width=image.width())

    def on_mouse_release(self, event):
        """Handle mouse release to stop dragging points for homography and crop."""
        self.dragging_point = None

    def is_close(self, point1, point2, threshold=10):
        """Check if two points are within a certain threshold distance."""
        return np.linalg.norm(np.array(point1) - np.array(point2)) < threshold

    def perform_homography(self, frame):
        """Perform homography transform and update the transformed image."""
        if len(self.src_points) == 4:
            if (self.homography_width.get() == '' or self.homography_height.get() == ''):  # Check if width and height are empty
                logging.error("Width and height must be set.")
                return frame
            try:
                # Get the target dimensions from the user input
                target_width = float(self.homography_width.get())
                target_height = float(self.homography_height.get())
            except ValueError:
                logging.error("Width and height must be valid numbers.")
                return frame
            
            self.src_points = self.sort_points_clockwise(self.src_points)

            src = np.array(self.src_points, dtype=np.float32)
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
                return frame
                logging.error(f"Error performing homography: {e}")

    def perform_crop(self, frame):
        """Perform cropping based on crop points and update the transformed image."""
        if len(self.crop_points) == 4:
            crop_points = np.array(self.crop_points, dtype=np.float32)
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

    def update_transformed_display(self, frame):
        """Update the transformed frame displayed in the UI."""
        image = Image.fromarray(frame)
        image = ImageTk.PhotoImage(image)
        self.frm_transformed.configure(image=image)
        self.frm_transformed.image = image

    def sort_points_clockwise(self, pts):
        # Calculate the center of the quadrilateral
        center = np.mean(pts, axis=0)

        # Sort the points based on their angle relative to the center
        def angle_from_center(pt):
            return np.arctan2(pt[1] - center[1], pt[0] - center[0])

        sorted_pts = sorted(pts, key=angle_from_center)
        return sorted_pts

    async def update_frame(self):
        """Update the frame displayed in the UI."""
        while not self.stop_event.is_set():
            try:
                if not self.frame_queue.empty():
                    frame = self.frame_queue.get()
                    self.current_frame = frame.copy()
                    self.update_frame_display(frame, draw_points=True)
                    temp_frame = frame.copy()
                    if self.enable_crop.get() and len(self.crop_points) == 4:
                        temp_frame = self.perform_crop(frame)
                    if self.enable_homography.get() and len(self.src_points) == 4:
                        temp_frame = self.perform_homography(temp_frame)
                    self.update_transformed_display(temp_frame)
                await asyncio.sleep(0.033)  # Approx 30 FPS
            except Exception as e:
                logging.error(f"Error updating frame: {e}")
                await asyncio.sleep(1)  # Try again after 1 second if there's an error
