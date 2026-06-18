import sys
import os
import json
import time
import shutil
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from functools import wraps


def resource_path(relative_path):
    """Get absolute path to bundled resource (read-only), works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS  # ignore
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def time_it(func):
    @wraps(func)  # Preserves the original function's metadata
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # Highest available resolution timer
        result = func(*args, **kwargs)
        end_time = time.perf_counter()

        execution_time = (end_time - start_time) / 60
        print(f"Function '{func.__name__}' took {execution_time:.2f} min to execute.")
        return result

    return wrapper


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


def set_volume(percentage):
    # 1. Get the speaker device
    device = AudioUtilities.GetSpeakers()

    # 2. Use the direct property instead of trying to manually .Activate() it
    interface = device.EndpointVolume

    # 3. Cast it to the standard volume control interface
    volume = interface.QueryInterface(IAudioEndpointVolume)

    # 4. Convert percentage (0-100) to a scalar value (0.0 to 1.0)
    scalar_volume = percentage / 100.0

    # 5. Set the master volume
    volume.SetMasterVolumeLevelScalar(scalar_volume, None)
    print(f"Volume successfully set to {percentage}%")
