import os
import json
from pathlib import Path

class SettingsManager:
    def __init__(self):
        self.settings_file = "app_settings.json"
        self.default_settings = {
            "cvr_directory": None
        }
        self.settings = self.load_settings()

    def load_settings(self):
        """Load settings from file or return default settings if file doesn't exist."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self.default_settings.copy()
        return self.default_settings.copy()

    def save_settings(self):
        """Save current settings to file."""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get_cvr_directory(self):
        """Get the CVR directory from settings or try to find the default location."""
        if self.settings["cvr_directory"] and os.path.exists(self.settings["cvr_directory"]):
            return self.settings["cvr_directory"]

        # Try to find default Steam directory
        default_path = self._find_default_cvr_directory()
        if default_path:
            self.settings["cvr_directory"] = default_path
            self.save_settings()
            return default_path

        return None

    def set_cvr_directory(self, directory):
        """Set and save the CVR directory."""
        self.settings["cvr_directory"] = directory
        self.save_settings()

    def _find_default_cvr_directory(self):
        """Try to find the default CVR directory in common Steam locations."""
        # Common Steam installation paths
        steam_paths = [
            os.path.expandvars("%ProgramFiles(x86)%/Steam"),
            os.path.expandvars("%ProgramFiles%/Steam"),
            "C:/Steam",
            "D:/Steam"
        ]

        for steam_path in steam_paths:
            if not os.path.exists(steam_path):
                continue

            # Look for CVR in the common Steam apps directory
            cvr_path = os.path.join(steam_path, "steamapps", "common", "ChilloutVR")
            if os.path.exists(cvr_path) and os.path.exists(os.path.join(cvr_path, "ChilloutVR.exe")):
                return cvr_path

        return None

    def get_profiles_directory(self):
        """Get the directory containing AAS profiles."""
        cvr_dir = self.get_cvr_directory()
        if not cvr_dir:
            return None

        profiles_dir = os.path.join(cvr_dir, "ChilloutVR_Data", "AvatarsAdvancedSettingsProfiles")
        if os.path.exists(profiles_dir):
            return profiles_dir
        return None
        
    def get_autologin_profile_path(self):
        """Get the path to the autologin profile file."""
        cvr_dir = self.get_cvr_directory()
        if not cvr_dir:
            return None
            
        autologin_path = os.path.join(cvr_dir, "ChilloutVR_Data", "autologin.profile")
        if os.path.exists(autologin_path):
            return autologin_path
        return None 