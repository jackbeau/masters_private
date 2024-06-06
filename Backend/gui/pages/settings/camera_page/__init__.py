"""
Author: Jack Beaumont
Date: 06/06/2024

This module defines the CameraPage class for managing the camera settings,
capturing video frames, and rendering the user interface.
"""

import logging
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import multiprocessing
import asyncio
from gui.core.constants.styles import text, colours
from gui.core.constants.standard_resolutions import standard_resolutions
import gui.pages.shared.video_utils
from gui.pages.shared.settings_manager import CameraSettingsManager
from multiprocessing import Manager
from gui.pages.settings.shared.video_processing import video_loop
from gui.pages.settings.shared.plot_processing import plot_loop

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class CameraPage(tk.Frame):
    NAME = "Camera"

    def __init__(self, parent, settings_file="settings.json", *args, **kwargs):
        """Initialize the CameraPage class.

        Args:
            parent (tk.Tk or tk.Frame): The parent widget.
            settings_file (str): The settings file name.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        tk.Frame.__init__(self, parent, *args, **kwargs)

        # Initialize attributes
        self.resizing = False
        self.stop_event = multiprocessing.Event()
        self.frame_queue = multiprocessing.Queue(maxsize=1)
        self.hist_queue = multiprocessing.Queue(maxsize=1)
        self.manager = Manager()
        self.settings = self.manager.dict()

        # Initialize settings manager
        self.settings_manager = CameraSettingsManager(settings_file)
        self.load_settings()

        # Get video device info and their maximum resolutions
        self.get_video_device_info()
        self.configure_video_device()

        # Start video capture and processing
        self.start_processes()

        # Start asynchronous tasks for updating frame and plot
        self.start_async_tasks()

        # Render the UI
        self.render()

    def get_video_device_info(self):
        """Get information about the video device."""
        self.video_devices = gui.pages.shared.video_utils.get_video_devices()
        try:
            device = next(
                (
                    device
                    for device in self.video_devices
                    if device["uniqueID"] == self.video_device_id
                ),
                None,
            )
            if device:
                self.video_device_name = device["localizedName"]
                self.video_device_position = device["position"]
                logging.info(
                    f"Selected device position: {self.video_device_position}"
                )
                self.update_settings_queue()
                return
            self.video_device_position = None
            self.video_device_name = None
            self.update_settings_queue()
        except ValueError:
            self.video_device_position = None
            self.video_device_name = None
            logging.error(f"Device with ID {self.video_device_id} not found.")

    def load_settings(self):
        """Load settings from the settings manager."""
        camera_settings = self.settings_manager.get_camera_settings()
        self.video_device_id = camera_settings.get("video_device_id", 0)
        self.rotation = camera_settings.get("rotation", 0)
        self.res = camera_settings.get("resolution", ())
        self.mirror_x = tk.IntVar(value=camera_settings.get("mirror_x", 0))
        self.mirror_y = tk.IntVar(value=camera_settings.get("mirror_y", 0))
        self.clahe = tk.IntVar(value=camera_settings.get("clahe", 0))
        self.clahe_clip_limit = tk.DoubleVar(
            value=camera_settings.get("clahe_clip_limit", 40)
        )
        self.brightness = tk.DoubleVar(
            value=camera_settings.get("brightness", 50)
        )
        self.exposure = tk.DoubleVar(value=camera_settings.get("exposure", 50))
        self.contrast = tk.DoubleVar(value=camera_settings.get("contrast", 50))
        self.saturation = tk.DoubleVar(
            value=camera_settings.get("saturation", 50)
        )

    def save_settings(self, *args):
        """Save current settings to the settings manager."""
        settings = {
            "video_device_id": self.video_device_id,
            "video_device_pos": self.video_device_position,
            "resolution": self.res,
            "rotation": self.rotation,
            "mirror_x": self.mirror_x.get(),
            "mirror_y": self.mirror_y.get(),
            "clahe": self.clahe.get(),
            "clahe_clip_limit": self.clahe_clip_limit.get(),
            "brightness": self.brightness.get(),
            "exposure": self.exposure.get(),
            "contrast": self.contrast.get(),
            "saturation": self.saturation.get(),
        }
        self.settings_manager.save_camera_settings(settings)
        self.update_settings_queue()

    def update_settings_queue(self):
        """Update the settings queue with current settings."""
        self.settings.update(
            {
                "video_device_id": self.video_device_id,
                "video_device_pos": self.video_device_position,
                "resolution": self.res,
                "rotation": self.rotation,
                "mirror_x": self.mirror_x.get(),
                "mirror_y": self.mirror_y.get(),
                "clahe": self.clahe.get(),
                "clahe_clip_limit": self.clahe_clip_limit.get(),
                "brightness": self.brightness.get(),
                "exposure": self.exposure.get(),
                "contrast": self.contrast.get(),
                "saturation": self.saturation.get(),
            }
        )

    def close(self):
        """Handle closing of the camera page."""
        self.stop_event.set()
        self.video_process.terminate()
        self.video_process.join()  # Ensure the process terminates
        self.plot_process.terminate()
        self.plot_process.join()  # Ensure the process terminates

    def configure_video_device(self):
        """Configure video device based on current settings."""
        if self.video_device_position is not None:
            self.max_res = gui.pages.shared.video_utils.get_max_resolution(
                self.video_device_position
            )
        else:
            self.max_res = None
        if self.max_res is not None:
            self.res_list = gui.pages.shared.video_utils.filter_resolutions(
                self.max_res, standard_resolutions
            )
            self.video_device_str = tk.StringVar(value=self.video_device_name)
        else:
            self.res_list = None
            self.video_device_str = tk.StringVar(value="")
        if not self.res:
            if self.res_list is not None:
                self.res = self.res_list[0]
                self.res_str = tk.StringVar(
                    value=f"{self.res[0]}x{self.res[1]}"
                )
            else:
                self.res_str = tk.StringVar(value="")
        else:
            self.res_str = tk.StringVar(value=f"{self.res[0]}x{self.res[1]}")

    def start_processes(self):
        """Start video and plot processing in separate processes."""
        self.stop_event.clear()
        self.video_process = multiprocessing.Process(
            target=video_loop,
            args=(self.frame_queue, self.stop_event, self.settings),
        )
        self.plot_process = multiprocessing.Process(
            target=plot_loop,
            args=(
                self.hist_queue,
                self.frame_queue,
                self.stop_event,
                self.settings,
            ),
        )
        self.video_process.start()
        self.plot_process.start()

    def start_async_tasks(self):
        """Start asynchronous tasks for updating frame and plot."""
        asyncio.create_task(self.update_frame())
        asyncio.create_task(self.update_plot())

    def rst_colour(self):
        """Reset color settings to default values."""
        self.brightness.set(50)
        self.exposure.set(50)
        self.contrast.set(50)
        self.saturation.set(50)
        self.clahe_clip_limit.set(40)
        self.save_settings()

    def render(self):
        """Render the GUI."""
        self.master.bind(
            "<Configure>",
            lambda event: (
                setattr(self, "resizing", True),
                self.master.after(
                    1000, lambda: setattr(self, "resizing", False)
                ),
            ),
        )

        # Camera feed placeholder
        self.frm_video = ttk.Label(
            self, image=None, anchor="center", justify="center"
        )
        self.frm_video.pack(expand=True, fill="x", side="top", pady=(0, 12))

        # Video input title
        frm_row_1 = tk.Frame(self, background=colours.off_black_80)
        frm_row_1.pack(fill="x", pady=(0, 4))

        lbl_vid_input = text(
            frm_row_1, text="Video Input", style="PageHeading2"
        )
        lbl_vid_input.pack(side="left")

        # Frame for row
        frm_row_2 = tk.Frame(self, background=colours.off_black_80)
        frm_row_2.pack(side="top", fill="x", expand=True, pady=(0, 4))

        # Label for source settings and menu for source options
        lbl_source = text(frm_row_2, text="Source", style="PageText")
        lbl_source.pack(side="left", padx=(0, 8))

        self.source_menu = ttk.OptionMenu(
            frm_row_2,
            self.video_device_str,
            command=self.select_video_device,
            style="Label.TMenubutton",
        )
        self.source_menu.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Label for resolution settings and menu for resolution options
        lbl_resolution = text(frm_row_2, text="Resolution", style="PageText")
        lbl_resolution.pack(side="left", padx=(0, 8))

        self.res_menu = ttk.OptionMenu(
            frm_row_2,
            self.res_str,
            command=self.change_res,
            style="Label.TMenubutton",
        )

        self.res_menu.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Rotate button
        btn_rotate = ttk.Button(
            frm_row_2,
            text="Rotate 90°",
            command=self.rotate_camera,
            style="Label.TButton",
        )
        btn_rotate.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Frame for row
        frm_row_3 = tk.Frame(self, background=colours.off_black_80)
        frm_row_3.pack(side="top", fill="x", expand=True, pady=(0, 8))

        # Mirror buttons
        btn_mirror_horizontal = ttk.Checkbutton(
            frm_row_3,
            text="Mirror Horizontal",
            style="Label.TCheckbutton",
            variable=self.mirror_x,
            onvalue=1,
            offvalue=0,
            command=self.save_settings,
        )
        btn_mirror_horizontal.pack(side="left", padx=(0, 8))

        btn_mirror_vertical = ttk.Checkbutton(
            frm_row_3,
            text="Mirror Vertical",
            style="Label.TCheckbutton",
            variable=self.mirror_y,
            onvalue=1,
            offvalue=0,
            command=self.save_settings,
        )
        btn_mirror_vertical.pack(side="left")

        # Colour adjustment title
        frm_row_4 = tk.Frame(self, background=colours.off_black_80)
        frm_row_4.pack(fill="x", pady=(0, 4))

        lbl_col_adj = text(
            frm_row_4, text="Colour Adjustment Histogram", style="PageHeading2"
        )
        lbl_col_adj.pack(side="left")

        # Frame for row
        frm_row_5 = tk.Frame(self, background=colours.off_black_80)
        frm_row_5.pack(side="top", fill="x", expand=True)

        # Histogram placeholder
        self.hist_label = ttk.Label(
            frm_row_5,
            image=None,
            anchor="center",
            justify="center",
            background=colours.off_black_80,
        )
        self.hist_label.pack(expand=True, fill="x", side="left", padx=(0, 8))

        # Frame for colour settings sidebar
        frm_row_5_col_1 = tk.Frame(frm_row_5, background=colours.off_black_80)
        frm_row_5_col_1.pack(fill="y", side="left", padx=(0, 8))

        # CLAHE equalisation checkbutton
        btn_clahe = ttk.Checkbutton(
            frm_row_5_col_1,
            text="CLAHE Equalisation",
            style="Label.TCheckbutton",
            variable=self.clahe,
            onvalue=1,
            offvalue=0,
            command=self.save_settings,
        )
        btn_clahe.grid(row=0, column=0, columnspan=2, sticky="ew")

        # CLAHE clipLimit settings slider
        lbl_clahe_clip_limit = text(
            frm_row_5_col_1, text="CLAHE Clip Limit", style="PageText"
        )
        lbl_clahe_clip_limit.grid(row=1, column=0, sticky="w", padx=(0, 4))
        scl_clahe_clip_limit = ttk.Scale(
            frm_row_5_col_1,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.clahe_clip_limit,
            command=self.save_settings,
        )
        scl_clahe_clip_limit.grid(row=1, column=1)

        # Brightness settings slider
        lbl_brightness = text(
            frm_row_5_col_1, text="Brightness", style="PageText"
        )
        lbl_brightness.grid(row=2, column=0, sticky="w", padx=(0, 4))
        scl_brightness = ttk.Scale(
            frm_row_5_col_1,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.brightness,
            command=self.save_settings,
        )
        scl_brightness.grid(row=2, column=1)

        # Exposure settings slider
        lbl_exposure = text(frm_row_5_col_1, text="Exposure", style="PageText")
        lbl_exposure.grid(row=3, column=0, sticky="w", padx=(0, 4))
        scl_exposure = ttk.Scale(
            frm_row_5_col_1,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.exposure,
            command=self.save_settings,
        )
        scl_exposure.grid(row=3, column=1)

        # Contrast settings slider
        lbl_contrast = text(frm_row_5_col_1, text="Contrast", style="PageText")
        lbl_contrast.grid(row=4, column=0, sticky="w", padx=(0, 4))
        scl_contrast = ttk.Scale(
            frm_row_5_col_1,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.contrast,
            command=self.save_settings,
        )
        scl_contrast.grid(row=4, column=1)

        # Saturation settings slider
        lbl_saturation = text(
            frm_row_5_col_1, text="Saturation", style="PageText"
        )
        lbl_saturation.grid(row=5, column=0, sticky="w", padx=(0, 4))
        scl_saturation = ttk.Scale(
            frm_row_5_col_1,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.saturation,
            command=self.save_settings,
        )
        scl_saturation.grid(row=5, column=1)

        # Reset colour settings button
        btn_rst_colour = ttk.Button(
            frm_row_5_col_1,
            text="Reset",
            command=self.rst_colour,
            style="Label.TButton",
        )
        btn_rst_colour.grid(row=6, column=0, columnspan=2, sticky="ew", pady=8)

        # Generate menu options
        self.gen_res_options(self.res_list)
        self.gen_src_options(self.video_devices)

    def gen_res_options(self, res_list):
        """Generate resolution options for the resolution menu.

        Args:
            res_list (list): List of available resolutions.
        """
        self.res_menu["menu"].delete(0, "end")
        if res_list is not None:
            for res in self.res_list:
                self.res_menu["menu"].add_command(
                    label=f"{res[0]}x{res[1]}",
                    command=tk._setit(
                        self.res_str, f"{res[0]}x{res[1]}", self.change_res
                    ),
                )

    def gen_src_options(self, src_list):
        """Generate source options for the source menu.

        Args:
            src_list (list): List of available video sources.
        """
        self.source_menu["menu"].delete(0, "end")
        for src in src_list:
            self.source_menu["menu"].add_command(
                label=src["localizedName"],
                command=tk._setit(
                    self.video_device_str,
                    src["localizedName"],
                    self.select_video_device,
                ),
            )

    def change_res(self, selected_res):
        """Handle resolution change.

        Args:
            selected_res (str): The selected resolution in 'WIDTHxHEIGHT'
            format.
        """
        width, height = map(int, selected_res.split("x"))
        self.res = (width, height)
        self.save_settings()
        logging.info(f"Resolution changed to: {self.res}")

    def select_video_device(self, device_idn):
        """Handle video device selection.

        Args:
            device_idn (str): The identifier of the selected video device.
        """
        if device_idn != self.video_device_name:
            new_device = next(
                (
                    i
                    for i in self.video_devices
                    if i["localizedName"] == device_idn
                ),
                None,
            )
            self.video_device_name = new_device["localizedName"]
            self.video_device_id = new_device["uniqueID"]
            self.video_device_position = new_device["position"]
            self.save_settings()
            try:
                self.stop_event.set()
                self.video_process.terminate()
                self.video_process.join()  # Ensure the process terminates
                self.plot_process.terminate()
                self.plot_process.join()  # Ensure the process terminates
                self.stop_event.clear()

                # Reinitialize the queues to ensure they are clean
                self.frame_queue = multiprocessing.Queue(maxsize=1)
                self.hist_queue = multiprocessing.Queue(maxsize=1)

                # Restart processes
                self.start_processes()

                self.configure_video_device()
                self.gen_res_options(self.res_list)
            except Exception as e:
                logging.error(f"Error selecting camera device: {e}")

    async def update_frame(self):
        """Update the frame displayed in the UI."""
        while not self.stop_event.is_set():
            try:
                if not self.frame_queue.empty():
                    frame, _ = self.frame_queue.get()
                    image = Image.fromarray(frame)
                    image = ImageTk.PhotoImage(image)
                    self.frm_video.configure(image=image)
                    self.frm_video.image = image
                await asyncio.sleep(0.033)  # Approx 30 FPS
            except Exception as e:
                logging.error(f"Error updating frame: {e}")
                await asyncio.sleep(
                    1
                )  # Try again after 1 second if there's an error

    async def update_plot(self):
        """Update the plot displayed in the UI."""
        while not self.stop_event.is_set():
            try:
                if not self.hist_queue.empty():
                    hist_image = self.hist_queue.get()
                    photo = ImageTk.PhotoImage(hist_image)
                    self.hist_label.configure(image=photo)
                    self.hist_label.image = photo
                await asyncio.sleep(0.1)  # Update every 100ms
            except Exception as e:
                logging.error(f"Error updating plot: {e}")
                await asyncio.sleep(
                    1
                )  # Try again after 1 second if there's an error

    def rotate_camera(self):
        """Rotate the camera image by 90 degrees."""
        self.rotation = (self.rotation + 1) % 4
        self.save_settings()
