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