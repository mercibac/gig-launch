import sys
import os
import json
import shutil


def resource_path(relative_path):
    """Get absolute path to bundled resource (read-only), works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS  # ignore
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def _get_persistent_dir():
    """Get the writable directory for user files (next to the .exe or script)."""
    if getattr(sys, "frozen", False):
        # Running as compiled executable — use the folder containing the .exe
        return os.path.dirname(sys.executable)
    else:
        # Running as script — use the script's own directory
        return os.path.abspath(".")


# The settings file lives next to the executable, NOT inside _MEIPASS
CONFIG_FILE = os.path.join(_get_persistent_dir(), "settings.json")


def _ensure_settings_file():
    """On first run after install, copy the bundled default settings to the persistent location."""
    if not os.path.exists(CONFIG_FILE):
        bundled = resource_path("settings.json")
        if os.path.exists(bundled) and os.path.normpath(bundled) != os.path.normpath(
            CONFIG_FILE
        ):
            shutil.copy2(bundled, CONFIG_FILE)


def load_config():
    """Load and return the current config from disk (always fresh)."""
    _ensure_settings_file()
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)
