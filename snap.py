import pygetwindow as gw
import pyautogui
import time


def snap_gig_windows():
    time.sleep(30)
    print("Snapping windows into position...")

    # 1. Get your exact screen dimensions dynamically
    screen_width, screen_height = pyautogui.size()
    half_width = screen_width // 2

    # Give the apps a couple of seconds to ensure their windows are fully registered by Windows
    time.sleep(2)

    # ---------------------------------------------------------
    # 2. Anchor Open Stage Control to the Left
    # ---------------------------------------------------------
    # Look for any window title that contains "Open Stage Control"
    osc_windows = gw.getWindowsWithTitle("Open Stage Control v1.30.1")

    if osc_windows:
        osc_win = osc_windows[0]
        try:
            osc_win.restore()  # Pulls it out of full-screen if it launched maximized
            osc_win.moveTo(0, 0)  # Top-left corner
            osc_win.resizeTo(half_width, screen_height)  # Fill exactly the left half
            print("Open Stage Control anchored to the left.")
        except Exception as e:
            print(f"Error sizing Open Stage Control: {e}")
    else:
        print("Could not find Open Stage Control window to snap.")

    # ---------------------------------------------------------
    # 3. Anchor Gig Performer to the Right
    # ---------------------------------------------------------
    gp_windows = gw.getWindowsWithTitle("Keyboard_Live")

    if gp_windows:
        gp_win = gp_windows[0]
        try:
            gp_win.restore()
            # Move it to start exactly halfway across the screen
            gp_win.moveTo(half_width, 0)
            gp_win.resizeTo(half_width, screen_height)  # Fill exactly the right half
            print("Gig Performer anchored to the right.")
        except Exception as e:
            print(f"Error sizing Gig Performer: {e}")
    else:
        print("Could not find Gig Performer window to snap.")


if __name__ == "__main__":
    snap_gig_windows()
