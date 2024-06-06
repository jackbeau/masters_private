"""
Author: Jack Beaumont
Date: 06/06/2024

This module provides functionality for managing settings stored in a JSON file.
It includes classes for managing general settings, as well as specific settings
for camera and stage zones.

Classes:
    SettingsManager: Manages loading and saving of general settings.
    CameraSettingsManager: Manages loading and saving of camera settings.
    StageZoneSettingsManager: Manages loading and saving of stage zone
                              settings.
"""

import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SettingsManager:
    """
    A class to manage the loading and saving of settings to a JSON file.

    Attributes:
        settings_file (str): The path to the settings file.
    """

    def __init__(self, settings_file="settings.json"):
        """
        Initializes the SettingsManager with the given settings file.

        Args:
            settings_file (str): The path to the settings file. Defaults to
                                 "settings.json".
        """
        self.settings_file = settings_file

    def load_settings(self):
        """
        Loads the settings from the JSON file.

        Returns:
            dict: The loaded settings. If the file is not found, an empty
                  dictionary is returned.
        """
        try:
            with open(self.settings_file, "r") as f:
                settings = json.load(f)
                logger.info(f"Settings loaded from {self.settings_file}")
                return settings
        except FileNotFoundError:
            logger.warning(
                f"{self.settings_file} not found. Returning empty settings."
            )
            return {}

    def save_settings(self, settings):
        """
        Saves the given settings to the JSON file.

        Args:
            settings (dict): The settings to save.
        """
        with open(self.settings_file, "w") as f:
            json.dump(settings, f, indent=4)
            logger.info(f"Settings saved to {self.settings_file}")


class CameraSettingsManager(SettingsManager):
    """
    A class to manage the loading and saving of camera settings.
    Inherits from SettingsManager.
    """

    def get_camera_settings(self):
        """
        Retrieves the camera settings from the loaded settings.

        Returns:
            dict: The camera settings. If not found, an empty dictionary is
                  returned.
        """
        settings = self.load_settings()
        return settings.get("camera", {})

    def save_camera_settings(self, camera_settings):
        """
        Saves the given camera settings to the settings file.

        Args:
            camera_settings (dict): The camera settings to save.
        """
        settings = self.load_settings()
        settings["camera"] = camera_settings
        self.save_settings(settings)


class StageZoneSettingsManager(SettingsManager):
    """
    A class to manage the loading and saving of stage zone settings.
    Inherits from SettingsManager.
    """

    def get_stage_zone_settings(self):
        """
        Retrieves the stage zone settings from the loaded settings.

        Returns:
            dict: The stage zone settings. If not found, an empty dictionary
                  is returned.
        """
        settings = self.load_settings()
        return settings.get("stage_zone", {})

    def save_stage_zone_settings(self, stage_zone_settings):
        """
        Saves the given stage zone settings to the settings file.

        Args:
            stage_zone_settings (dict): The stage zone settings to save.
        """
        settings = self.load_settings()
        settings["stage_zone"] = stage_zone_settings
        self.save_settings(settings)
