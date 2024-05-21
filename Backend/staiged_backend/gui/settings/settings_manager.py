from utils import SettingsManager

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