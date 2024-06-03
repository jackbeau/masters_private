import json

class SettingsManager:
    def __init__(self, settings_file="settings.json"):
        self.settings_file = settings_file

    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_settings(self, settings):
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)


class CameraSettingsManager(SettingsManager):
    def get_camera_settings(self):
        settings = self.load_settings()
        return settings.get("camera", {})

    def save_camera_settings(self, camera_settings):
        settings = self.load_settings()
        settings['camera'] = camera_settings
        self.save_settings(settings)


class StageZoneSettingsManager(SettingsManager):
    def get_stage_zone_settings(self):
        settings = self.load_settings()
        return settings.get("stage_zone", {})

    def save_stage_zone_settings(self, stage_zone_settings):
        settings = self.load_settings()
        settings['stage_zone'] = stage_zone_settings
        self.save_settings(settings)