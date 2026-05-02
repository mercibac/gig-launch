import sys
import os
import json

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS  # ignore
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


CONFIG_FILE = resource_path("settings.json")


with open(CONFIG_FILE, "r") as f:
    CONFIG = json.load(f)

WIFI = CONFIG["hotspot_name"]
PHONE = CONFIG["phone_name"]
