import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import threading
import os
import sys
import json
import ctypes

# ---------------------------------------------------------
# IMPORT YOUR SCRIPTS AS MODULES
# ---------------------------------------------------------
import gig_launcher
import gig_close
from utils import CONFIG_FILE


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# --- Configuration Manager ---
DEFAULT_CONFIG = {
    "phone_name": "SMART PHONE",
    "hotspot_name": "SHARED ACCESS POINT",
    "osc_file_path": "",
}

# --- UI Theme Colors ---
BG_COLOR = "#2b2b2b"
TEXT_BG = "#1e1e1e"
TEXT_FG = "#d4d4d4"
BTN_BLUE = "#007acc"
BTN_BLUE_HOVER = "#005c99"
BTN_GRAY = "#555555"
BTN_GRAY_HOVER = "#333333"


# ==========================================
# UTILITY FUNCTIONS
# ==========================================
def load_settings():
    """Loads settings from JSON, or creates/repairs it if missing or corrupted."""
    if not os.path.exists(CONFIG_FILE):
        save_settings(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        # If the file is empty or corrupted, print the warning AND overwrite it with a fresh copy
        print(f"Warning: settings.json is empty or corrupted. Repairing... ({e})")
        save_settings(DEFAULT_CONFIG)
        return DEFAULT_CONFIG


def save_settings(data):
    """Saves the dictionary to the JSON file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ==========================================
# CONSOLE REDIRECTOR CLASS
# ==========================================
class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        # We use the text_widget's own .after() method to safely update the UI thread
        self.text_widget.after(0, self._append_text, string)

    def _append_text(self, string):
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state=tk.DISABLED)

    def flush(self):
        pass


# ==========================================
# SETTINGS MODAL CLASS
# ==========================================
# ==========================================
# SETTINGS MODAL CLASS
# ==========================================
# ==========================================
# SETTINGS MODAL CLASS
# ==========================================
class SettingsModal:
    def __init__(self, parent, current_settings, on_save_callback):
        self.window = tk.Toplevel(parent)
        self.window.title("Configuration Settings")
        self.window.configure(bg=BG_COLOR)

        # 1. Prevent resizing to keep the layout strict
        self.window.resizable(False, False)

        # 2. Set a fixed, slightly wider default width to fit everything perfectly
        modal_width = 650
        modal_height = 300

        # --- Center the modal over the main UI ---
        parent.update_idletasks()
        p_x = parent.winfo_rootx()
        p_y = parent.winfo_rooty()
        p_width = parent.winfo_width()
        p_height = parent.winfo_height()

        pos_x = p_x + int((p_width / 2) - (modal_width / 2))
        pos_y = p_y + int((p_height / 2) - (modal_height / 2))

        self.window.geometry(f"{modal_width}x{modal_height}+{pos_x}+{pos_y}")

        self.window.transient(parent)
        self.window.grab_set()

        self.on_save_callback = on_save_callback

        # --- Layout Container ---
        container = tk.Frame(self.window, bg=BG_COLOR)
        container.pack(expand=True)

        # 3. Increase entry width slightly so file paths aren't cut off
        label_kwargs = {"bg": BG_COLOR, "fg": TEXT_FG, "font": ("Segoe UI", 10)}
        entry_kwargs = {"font": ("Segoe UI", 10), "width": 35}

        # --- Phone Name ---
        # Removed sticky="e" so the label naturally centers in its grid space
        tk.Label(container, text="Phone Name (KDE Connect):", **label_kwargs).grid(
            row=0, column=0, padx=10, pady=12
        )
        self.entry_phone = tk.Entry(container, **entry_kwargs)
        self.entry_phone.insert(0, current_settings.get("phone_name", ""))
        self.entry_phone.grid(row=0, column=1, padx=10, pady=12)

        # --- Hotspot Name ---
        tk.Label(container, text="Hotspot Name (SSID):", **label_kwargs).grid(
            row=1, column=0, padx=10, pady=12
        )
        self.entry_hotspot = tk.Entry(container, **entry_kwargs)
        self.entry_hotspot.insert(0, current_settings.get("hotspot_name", ""))
        self.entry_hotspot.grid(row=1, column=1, padx=10, pady=12)

        # --- OSC File Path ---
        tk.Label(container, text="OSC File Path:", **label_kwargs).grid(
            row=2, column=0, padx=10, pady=12
        )
        self.entry_filepath = tk.Entry(container, **entry_kwargs)
        self.entry_filepath.insert(0, current_settings.get("osc_file_path", ""))
        self.entry_filepath.grid(row=2, column=1, padx=10, pady=12)

        # --- Save Button ---
        save_btn = tk.Button(
            container,
            text="SAVE SETTINGS",
            bg=BTN_BLUE,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            relief="flat",
            command=self.save_and_close,
        )
        save_btn.grid(row=3, column=0, columnspan=2, pady=(25, 10), ipadx=30, ipady=6)

    def save_and_close(self):
        new_settings = {
            "phone_name": self.entry_phone.get().strip(),
            "hotspot_name": self.entry_hotspot.get().strip(),
            "osc_file_path": self.entry_filepath.get().strip(),
        }

        # Validate that only the mandatory fields are filled out
        if not new_settings["phone_name"] or not new_settings["hotspot_name"]:
            messagebox.showwarning(
                "Warning",
                "Phone Name and Hotspot Name are mandatory.",
                parent=self.window,
            )
            return

        self.on_save_callback(new_settings)
        self.window.destroy()


# ==========================================
# MAIN APPLICATION CLASS
# ==========================================
class GigControlApp:
    def __init__(self, root):
        self.root = root
        self.settings = load_settings()

        # --- UI Initialization ---
        self.setup_window()
        self.build_widgets()

        # --- Terminal Hijack ---
        sys.stdout = ConsoleRedirector(self.console_output)
        sys.stderr = ConsoleRedirector(self.console_output)

        print("System initialized. Awaiting command...\n")

    def setup_window(self):
        self.root.title("Gig Control Center")
        try:
            self.root.iconbitmap(resource_path("icon.ico"))
        except Exception:
            pass

        app_width, app_height = 800, 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (app_width / 2))
        y_coordinate = int((screen_height / 2) - (app_height / 2))

        self.root.geometry(f"{app_width}x{app_height}+{x_coordinate}+{y_coordinate}")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

    def build_widgets(self):
        # 1. Top Button Frame (Anchored to the Top)
        btn_frame = tk.Frame(self.root, bg=BG_COLOR)
        btn_frame.pack(side=tk.TOP, pady=20, padx=20, fill=tk.X)

        self.btn_clear = tk.Button(
            btn_frame,
            text="CLEAR DECK",
            font=("Segoe UI", 18, "bold"),
            bg=BTN_GRAY,
            fg="white",
            activebackground=BTN_GRAY_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.run_clear_script,
            width=20,
        )
        self.btn_clear.pack(side=tk.LEFT, fill=tk.Y)

        self.btn_launch = tk.Button(
            btn_frame,
            text="LAUNCH GIG RIG",
            font=("Segoe UI", 24, "bold"),
            bg=BTN_BLUE,
            fg="white",
            activebackground=BTN_BLUE_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.run_launch_script,
        )
        self.btn_launch.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # 2. Bottom Settings Frame (PACKED BEFORE THE CONSOLE!)
        bottom_frame = tk.Frame(self.root, bg=BG_COLOR)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 20))

        self.btn_settings = tk.Button(
            bottom_frame,
            text="⚙ Settings",
            font=("Segoe UI", 10),
            bg=BTN_GRAY,
            fg="white",
            activebackground=BTN_GRAY_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.open_settings_window,
            padx=10,
        )
        self.btn_settings.pack(side=tk.RIGHT)

        # 3. Scrolled Text Console (Now safely squeezed in the middle)
        self.console_output = scrolledtext.ScrolledText(
            self.root,
            bg=TEXT_BG,
            fg=TEXT_FG,
            font=("Consolas", 14),
            relief="flat",
            padx=10,
            pady=10,
        )
        self.console_output.pack(
            side=tk.TOP, padx=20, pady=(0, 10), fill=tk.BOTH, expand=True
        )

    # --- Button Logic ---
    def lock_buttons(self, status_text):
        self.btn_launch.config(state=tk.DISABLED, text=status_text, bg=BTN_BLUE_HOVER)
        self.btn_clear.config(state=tk.DISABLED, bg=BTN_GRAY_HOVER)

    def unlock_buttons(self):
        self.btn_launch.config(state=tk.NORMAL, text="LAUNCH GIG RIG", bg=BTN_BLUE)
        self.btn_clear.config(state=tk.NORMAL, text="CLEAR DECK", bg=BTN_GRAY)
        print("\n--- SYSTEM READY ---")

    def run_launch_script(self):
        self.lock_buttons("INITIALIZING...")
        self.clear_console()
        threading.Thread(
            target=self.execute_module, args=(gig_launcher.main,), daemon=True
        ).start()

    def run_clear_script(self):
        self.lock_buttons("CLEARING...")
        self.clear_console()
        threading.Thread(
            target=self.execute_module, args=(gig_close.main,), daemon=True
        ).start()

    def clear_console(self):
        self.console_output.configure(state=tk.NORMAL)
        self.console_output.delete(1.0, tk.END)
        self.console_output.configure(state=tk.DISABLED)

    def execute_module(self, target_function):
        try:
            target_function()
        except Exception as e:
            print(f"\nSYSTEM ERROR: {e}")
        finally:
            self.root.after(0, self.unlock_buttons)

    # --- Settings Logic ---
    def open_settings_window(self):
        SettingsModal(self.root, self.settings, self.update_settings)

    def update_settings(self, new_settings):
        self.settings = new_settings
        save_settings(self.settings)
        print("\nSettings successfully updated and saved to settings.json.")


# ==========================================
# APP ENTRY POINT
# ==========================================
if __name__ == "__main__":
    # Taskbar Fix
    my_app_id = "gig_control.rig.launcher.1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

    # Initialize Tkinter and Application
    root = tk.Tk()
    app = GigControlApp(root)
    root.mainloop()
