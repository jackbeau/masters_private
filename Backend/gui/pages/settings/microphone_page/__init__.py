"""
Author: Jack Beaumont
Date: 06/06/2024

This module defines the MicrophonePage class for managing microphone settings
in a Tkinter GUI.
"""

import tkinter as tk
from tkinter import ttk
from gui.core.constants.styles import text, colours
from gui.core.constants.standard_resolutions import standard_resolutions
import gui.pages.shared.video_utils
import logging
from gui.pages.shared.settings_manager import SettingsManager
import pyaudio

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MicrophonePage(tk.Frame):
    """
    Microphone settings panel widget
    """

    NAME = "Microphone"

    def __init__(self, parent, settings_file="settings.json", *args, **kwargs):
        """
        Initialise the microphone panel widget.

        :param parent: parent widget
        :type parent: tkinter widget
        :param settings_file: path to settings, defaults to "settings.json"
        :type settings_file: str, optional
        """
        super().__init__(parent, *args, **kwargs)

        self.settings_file = settings_file
        self.microphone_device = 0
        self.microphone_settings_manager = MicrophoneSettingsManager(
            settings_file
        )
        self.mic_device_str = tk.StringVar(value="")

        self.load_settings()
        self.render()
        self.gen_mic_options()

    def close(self) -> None:
        """
        Placeholder for close action. To be implemented as needed.
        """
        pass

    def load_settings(self) -> None:
        """
        Load microphone settings.
        """
        settings = self.microphone_settings_manager.get_microphone_settings()
        self.microphone_device = settings.get("microphone_device", 0)
        logging.info("Loaded microphone settings.")

    def save_settings(self, *args) -> None:
        """
        Save microphone settings.
        """
        settings = {"microphone_device": self.microphone_device}
        self.microphone_settings_manager.save_microphone_settings(settings)
        logging.info("Saved microphone settings.")

    def render(self) -> None:
        """
        Render the GUI.
        """
        frm_row_2 = tk.Frame(self, background=colours.off_black_80)
        frm_row_2.pack(side="top", fill="x", expand=True, pady=(0, 4))

        lbl_source = text(frm_row_2, text="Microphone", style="PageText")
        lbl_source.pack(side="left", padx=(0, 8))

        self.mic_menu = ttk.OptionMenu(
            frm_row_2, self.mic_device_str, style="Label.TMenubutton"
        )
        self.mic_menu.config(width=20)
        self.mic_menu.pack(side="left", fill="x", expand=True, padx=(0, 8))

    def gen_mic_options(self) -> None:
        """
        Generate microphone options for OptionMenu.
        """
        p = pyaudio.PyAudio()
        devices = p.get_device_count()
        self.mic_menu["menu"].delete(0, "end")  # Delete old options

        for i in range(devices):
            device_info = p.get_device_info_by_index(i)
            if device_info.get("maxInputChannels") > 0:
                logging.info(
                    f"Microphone found: {device_info.get('name')}, "
                    f"Device Index: {device_info.get('index')}"
                )
                if device_info.get("index") == self.microphone_device:
                    self.mic_device_str.set(device_info.get("name"))

                self.mic_menu["menu"].add_command(
                    label=device_info.get("name"),
                    command=tk._setit(
                        self.mic_device_str,
                        device_info.get("name"),
                        lambda event, device=device_info.get("index"): (
                            setattr(self, "microphone_device", device),
                            self.save_settings(),
                        ),
                    ),
                )

    def set_audio_device(self, device_idx: str) -> None:
        """
        OptionMenu callback to change the audio device.

        :param device_idx: Audio device id in the format ("Device id")
        :type device_idx: str
        """
        device_idx = int(device_idx[7:]) - 1

        if device_idx != self.microphone_device:
            self.microphone_device = device_idx
            self.save_settings()
            try:
                self.start_video_capture(device_idx)
                logging.info(
                    f"Microphone device selected successfully: {device_idx}"
                )

                self.res_list = (
                    gui.pages.shared.video_utils.filter_resolutions(
                        self.max_res[device_idx], standard_resolutions
                    )
                )
                self.gen_res_options(self.res_list)
            except Exception as e:
                logging.error(f"Error selecting microphone device: {e}")


class MicrophoneSettingsManager(SettingsManager):
    def get_microphone_settings(self) -> dict:
        """
        Retrieve microphone settings from the settings file.

        :return: Microphone settings
        :rtype: dict
        """
        settings = self.load_settings()
        return settings.get("microphone", {})

    def save_microphone_settings(self, microphone_settings: dict) -> None:
        """
        Save microphone settings to the settings file.

        :param microphone_settings: Microphone settings
        :type microphone_settings: dict
        """
        settings = self.load_settings()
        settings["microphone"] = microphone_settings
        self.save_settings(settings)
        logging.info("Microphone settings updated in the settings file.")
