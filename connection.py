import subprocess
import time


def get_current_wifi():
    """Asks Windows for the name of the currently connected Wi-Fi network."""
    try:
        # Run the Windows network shell command
        result = subprocess.check_output(
            ["netsh", "wlan", "show", "interfaces"], text=True
        )

        # Look through the output lines for the SSID
        for line in result.split("\n"):
            # We want the 'SSID' line, but not the 'BSSID' (MAC address) line
            if "SSID" in line and "BSSID" not in line:
                # Split the line at the colon and grab the network name
                return line.split(":")[1].strip()

    except subprocess.CalledProcessError:
        print("Error checking Wi-Fi status.")
        return None

    return None


def connect_to_network(ssid_name):
    """Forces Windows to connect to a known Wi-Fi profile."""
    print(f"Attempting to connect to '{ssid_name}'...")
    try:
        # This tells Windows to use the saved profile for this network name
        subprocess.run(
            ["netsh", "wlan", "connect", f"name={ssid_name}"],
            check=True,
            capture_output=True,
        )

        # Give Windows a few seconds to negotiate the IP address with your phone
        print("Waiting for connection to stabilize...")
        time.sleep(5)

    except subprocess.CalledProcessError:
        print(
            f"Failed to connect. Make sure the profile for '{ssid_name}' is saved on this PC."
        )


def ensure_correct_network(target_ssid):
    """The main logic to check and switch networks."""
    print("Checking network connection...")
    current_network = get_current_wifi()

    if current_network == target_ssid:
        print(f"Success: PC is already connected to '{target_ssid}'.")
        return True
    else:
        if current_network:
            print(f"Warning: Connected to the wrong network ('{current_network}').")
        else:
            print("Warning: Not connected to any Wi-Fi network.")

        connect_to_network(target_ssid)

        # Verify the connection worked
        if get_current_wifi() == target_ssid:
            print(f"Success: Successfully switched to '{target_ssid}'.")
            return True
        else:
            print(f"Error: Could not connect to '{target_ssid}'. Halting gig setup.")
            return False


if __name__ == "__main__":
    # Your target phone hotspot name
    target_network = "MERBAC PRO"

    # Run the check
    network_ready = ensure_correct_network(target_network)

    if network_ready:
        print(
            "\nNetwork is secure. Ready to launch Gig Performer and Open Stage Control..."
        )
        # Your gig launching code would go here
    else:
        print("\nPlease check your phone hotspot and try again.")
