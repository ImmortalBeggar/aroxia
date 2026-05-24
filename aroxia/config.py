import json
import os

class ConfigManager:
    def __init__(self, config_file="config/settings.json"):
        self.config_file = config_file
        self.settings = self._load_settings()

    def _load_settings(self):
        default = {
            "voice": {"lang": "en", "slow": False},
            "stickers": {"enabled": True, "pack": "HotCherry"},
            "gifs": {"enabled": True},
            "search": {"enabled": True}
        }
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                return {**default, **json.load(f)}
        return default

    def save_settings(self):
        with open(self.config_file, "w") as f:
            json.dump(self.settings, f, indent=4)

    def get(self, category, key=None):
        if key:
            return self.settings.get(category, {}).get(key)
        return self.settings.get(category)

    def update(self, category, key, value):
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
        self.save_settings()
