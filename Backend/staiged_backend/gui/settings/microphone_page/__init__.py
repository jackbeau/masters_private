import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import threading
from gui.styles import text, colours
from utils.video_stream import VideoStream
from utils.standard_resolutions import standard_resolutions
import utils.video_utils
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import time
import json
import logging
from utils import SettingsManager
import pyaudio

class MicrophonePage(tk.Frame):
    """
    Microphone settings panel widget
    """
    NAME = "Microphone"

    def __init__(self, parent, settings_file="settings.json", *args, **kwargs):
        """
        Initialise the camera panel widget

        :param parent: parent widget
        :type parent: tkinter widget
        :param settings_file: path to settings, defaults to "settings.json"
        :type settings_file: str, optional
        """
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.load_settings()
        self.mic_device_str = tk.StringVar(value="")

        # Render GUI
        self.render()

        self.gen_mic_options()

    def close(self) -> None:
        pass

    def load_settings(self):
        """
        Load settings
        """
        self.microphone_settings_manager = MicrophoneSettingsManager("settings.json")
        settings = self.microphone_settings_manager.get_microphone_settings()

        self.microphone_device = settings.get('microphone_device', 0)

    def save_settings(self, *args):
        """
        Save settings
        """
        settings = {
            'microphone_device': self.microphone_device
        }
        self.microphone_settings_manager.save_microphone_settings(settings)

    def render(self):
        """
        Render the GUI
        """
        # Frame for row
        frm_row_2 = tk.Frame(self, background=colours.off_black_80)
        frm_row_2.pack(side="top", fill="x", expand=True, pady=(0, 4))

        # Label for source settings and menu for source options
        lbl_source = text(frm_row_2, text="Microphone", style="PageText")
        lbl_source.pack(side="left", padx=(0, 8))

        self.mic_menu = ttk.OptionMenu(
            frm_row_2,
            self.mic_device_str,
            style="Label.TMenubutton"
        )
        self.mic_menu.config(width=20)
        self.mic_menu.pack(side="left", fill="x", expand=True, padx=(0, 8))

    def gen_mic_options(self):
        """
        Generate mic options for OptionMenu
        """
        p = pyaudio.PyAudio()
        # Get the number of audio I/O devices
        devices = p.get_device_count()
        self.mic_menu['menu'].delete(0, 'end')  # Delete old options

        # Iterate through all devices
        for i in range(devices):
            # Get the device info
            device_info = p.get_device_info_by_index(i)
            # Check if this device is a microphone (an input device)
            if device_info.get('maxInputChannels') > 0:
                print(f"Microphone: {device_info.get('name')} , Device Index: {device_info.get('index')}")
                if device_info.get('index') == self.microphone_device:
                    self.mic_device_str.set(device_info.get('name'))

                self.mic_menu['menu'].add_command(
                    label=device_info.get('name'),
                    command=tk._setit(
                        self.mic_device_str,
                        device_info.get('name'),
                        lambda event, device=device_info.get('index'): (
                            setattr(self, 'microphone_device', device),
                            self.save_settings()
                        )
                    )
                )
                
    def set_audio_device(self, device_idx):
        """
        OptionMenu callback to change video device

        :param device_idx: video device id of format ("Device id")
        :type device_idx: str
        """
        # OptionMenu returns string, extract the device id
        device_idx = int(device_idx[7:])-1

        # If device is not currently selected
        if device_idx != self.video_device:
            # Initialize the new camera
            self.video_device = device_idx
            self.save_settings()
            try:
                self.start_video_capture(device_idx)
                logging.info(
                    "Camera device selected successfully:",
                    device_idx
                )

                # Update resolution OptionMenu
                self.res_list = utils.video_utils.filter_resolutions(
                    self.max_res[device_idx], standard_resolutions
                )
                self.gen_res_options(self.res_list)
            except Exception as e:
                logging.info("Error selecting camera device:", e)


class MicrophoneSettingsManager(SettingsManager):
    def get_microphone_settings(self):
        settings = self.load_settings()
        return settings.get("microphone", {})

    def save_microphone_settings(self, microphone_settings):
        settings = self.load_settings()
        settings['microphone'] = microphone_settings
        self.save_settings(settings)