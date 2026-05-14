import subprocess
import psutil
import socket
import time
import pyautogui
import pyperclip
import os
import sys
import glob
import connection
import snap
from utils import load_config


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS  # ignore
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_wifi_ip():
    """Finds the IPv4 address of the wireless adapter."""
    for interface, snics in psutil.net_if_addrs().items():
        # Looks for common Windows Wi-Fi interface names
        if "wi-fi" in interface.lower() or "wireless" in interface.lower():
            for snic in snics:
                if snic.family == socket.AF_INET:
                    return snic.address
    return None


def get_most_recent_file(directory, extension="*.json"):
    """Finds the most recently modified file in a target directory."""
    files = glob.glob(os.path.join(directory, extension))
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def get_osc_on_top():
    screen_width, screen_height = pyautogui.size()
    pyautogui.moveTo(screen_width / 2, screen_height - 1, duration=0.2)
    time.sleep(1)
    # icon_image = "osc_icon.png"
    icon_image = resource_path("osc_icon.png")

    try:
        icon_location = pyautogui.locateCenterOnScreen(icon_image, confidence=0.8)

        if icon_location:
            print("Icon found! Clicking it...")
            pyautogui.click(icon_location)
            time.sleep(1)
        else:
            print("Could not find the icon on the screen.")

    except pyautogui.ImageNotFoundException:
        print("PyAutoGUI could not locate the image.")


def open_url_on_phone(url, phone_name):
    """
    Sends a URL to a specific paired device via KDE Connect.
    """
    print(f"Sending {url} to {phone_name}...")

    refresh = ["kdeconnect-cli", "--refresh"]
    # The command uses --share to send the link, and --name to target the exact device
    command = ["kdeconnect-cli", "--share", url, "--name", phone_name]

    try:
        # Run the command silently in the background
        subprocess.run(refresh, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(command, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print("URL sent successfully! Your phone should wake up and open the browser.")

    except subprocess.CalledProcessError as e:
        print(
            f"Failed to send URL. Is KDE Connect running, paired, and connected? Error: {e}"
        )
    except FileNotFoundError:
        print(
            "Error: 'kdeconnect-cli' not found. Make sure the KDE Connect Windows app is installed and running."
        )


def load_the_most_recent_file():
    pyautogui.click(x=14, y=62)
    pyautogui.moveTo(x=99, y=100)
    pyautogui.moveTo(x=275, y=189)
    pyautogui.click(x=450, y=189)


def default_file_exists():
    config = load_config()
    gig_osc_file = config["osc_file_path"]
    file_exist = os.path.isfile(resource_path(gig_osc_file))

    if file_exist:
        return gig_osc_file
    else:
        return False


def launch_programs(phone_name):
    # ---------------------------------------------------------
    # 1. Software Paths
    # ---------------------------------------------------------
    gig_performer_path = (
        r"C:\Program Files\Plugin Alliance\Gig Performer 4\GigPerformer4.exe"
    )
    osc_path = (
        r"D:\Apps\portable\open-stage-control_1.30.1_win32-x64\open-stage-control.exe"
    )
    osc_sessions_dir = r"D:\BANK\Presets\Archives"

    # ---------------------------------------------------------
    # 2. Launch Applications
    # ---------------------------------------------------------
    print("Launching Gig Performer...")
    os.system(f'start "" "{gig_performer_path}"')

    print("Launching Open Stage Control...")
    os.system(f'start "" "{osc_path}"')

    # Wait for Open Stage Control's UI to fully load
    time.sleep(5)

    # ---------------------------------------------------------
    # 3. Grab IP and Format it
    # ---------------------------------------------------------
    ip_address = get_wifi_ip()
    if not ip_address:
        print("Could not find Wi-Fi IP address. Defaulting to localhost.")
        ip_address = "127.0.0.1"

    send_value = f"{ip_address}:54344"
    pyperclip.copy(send_value)
    print(f"Copied {send_value} to clipboard.")

    # ---------------------------------------------------------
    # 4. GUI Automation (Update coordinates for your screen!)
    # ---------------------------------------------------------

    get_osc_on_top()

    pyautogui.click(x=300, y=110)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)
    # Click the 'Play' button to launch the server
    pyautogui.click(x=62, y=59)
    time.sleep(3)  # Wait for the server to spin up

    # ---------------------------------------------------------
    # 5. Load the most recent file
    # ---------------------------------------------------------

    if not default_file_exists():
        load_the_most_recent_file()

    open_url_on_phone(f"http://{ip_address}:8080", phone_name)


def main():
    # ---------------------------------------------------------
    # 0. Load fresh settings every time (so UI changes apply immediately)
    # ---------------------------------------------------------
    config = load_config()
    target = config["hotspot_name"]

    # ---------------------------------------------------------
    # 1. Connect the PC to my mobile HotSpot
    # ---------------------------------------------------------
    network_ready = connection.ensure_correct_network(target)

    if network_ready:
        print(
            "\nNetwork is secure. Ready to launch Gig Performer and Open Stage Control..."
        )
        launch_programs(config["phone_name"])
        snap.snap_gig_windows()
    else:
        print("\nPlease check your phone hotspot and try again.")


if __name__ == "__main__":
    main()
