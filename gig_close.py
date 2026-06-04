import psutil
import pygetwindow as gw
import time
from switch_defender import switch_defender
from switch_sleep import switch_sleep
from utils import set_volume


def force_kill(target_processes):
    """Instantly terminates specific background processes."""
    print("--- Phase 1: Force Killing Gig Apps ---")
    for proc in psutil.process_iter(["name"]):
        try:
            process_name = proc.info["name"]
            # Check if the process name matches any in our target list
            if process_name and any(
                target.lower() in process_name.lower() for target in target_processes
            ):
                print(f"Force killing process: {process_name}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # The process might have already closed or we don't have permission
            pass

    # Give Windows a second to free up the network ports and audio drivers
    time.sleep(1)


def clear_the_deck(protected_titles):
    """Politely closes visual windows, skipping protected ones."""
    print("\n--- Phase 2: Politely Closing Other Windows ---")
    windows = gw.getAllWindows()

    for win in windows:
        if win.title:
            title_lower = win.title.lower()

            # 1. Skip if it's the Windows Desktop environment ("program manager")
            # 2. Skip if the title contains any of our protected words (like "firefox")
            if "program manager" not in title_lower and not any(
                protected in title_lower for protected in protected_titles
            ):
                print(f"Politely closing window: {win.title}")
                try:
                    win.close()
                    time.sleep(0.2)  # Short pause so Windows doesn't get overwhelmed
                except Exception as e:
                    print(f"  -> Could not close '{win.title}'. Error: {e}")


def main():
    switch_sleep("on")
    switch_defender("on")
    set_volume(50)
    # 1. Put the exact .exe names here for the apps that MUST die
    apps_to_nuke = ["GigPerformer4.exe", "open-stage-control.exe"]

    # 2. Put the window titles here for the apps that MUST stay open
    apps_to_protect = ["firefox", "gig control center", "wezterm"]

    force_kill(apps_to_nuke)
    clear_the_deck(apps_to_protect)

    print(
        "\nDone! Gig apps are completely terminated, background windows are closed, and Firefox is safe."
    )


if __name__ == "__main__":
    main()
