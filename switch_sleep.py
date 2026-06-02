import subprocess
import time


def switch_sleep(option):
    if option == "on":
        ac_minutes = 10
    if option == "off":
        ac_minutes = 0

    try:
        # Change Plugged in (AC) setting
        subprocess.run(
            ["powercfg", "/change", "standby-timeout-ac", str(ac_minutes)],
            check=True,
            capture_output=True,
        )

        subprocess.run(
            ["powercfg", "/change", "monitor-timeout-ac", str(ac_minutes)],
            check=True,
            capture_output=True,
        )

        # Change On Battery in (DC) setting
        subprocess.run(
            ["powercfg", "/change", "standby-timeout-dc", str(ac_minutes)],
            check=True,
            capture_output=True,
        )

        subprocess.run(
            ["powercfg", "/change", "monitor-timeout-dc", str(ac_minutes)],
            check=True,
            capture_output=True,
        )

        # Give Windows a few seconds to negotiate the IP address with your phone
        print("Screen settings has been changed successfully")
        time.sleep(1)

    except subprocess.CalledProcessError:
        print("Failed to change sleep settings")
