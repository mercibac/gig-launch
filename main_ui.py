import tkinter as tk
from tkinter import scrolledtext
import threading
import sys
import ctypes

# ---------------------------------------------------------
# IMPORT YOUR SCRIPTS AS MODULES
# (Ensure gig_launcher.py and gig_close.py are in the same folder)
# ---------------------------------------------------------
import gig_launcher
import gig_close


# 1. The same helper function we used for the image
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# 2. THE WINDOWS TASKBAR FIX
# Tell Windows this is a unique app so it doesn't group it with generic Python scripts
my_app_id = "gig_control.rig.launcher.1"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)


# --- UI Theme Colors ---
BG_COLOR = "#2b2b2b"
TEXT_BG = "#1e1e1e"
TEXT_FG = "#d4d4d4"
BTN_BLUE = "#007acc"
BTN_BLUE_HOVER = "#005c99"
BTN_GRAY = "#555555"
BTN_GRAY_HOVER = "#333333"


# -u-------------------------------------------------------
# TEXT REDIRECTION CLASS
# This intercepts all print() commands and sends them to the UI
# ---------------------------------------------------------
class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        # We use root.after to ensure UI updates happen on the main thread safely
        root.after(0, self._append_text, string)

    def _append_text(self, string):
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state=tk.DISABLED)

    def flush(self):
        pass  # Required for sys.stdout compatibility


# ---------------------------------------------------------
# EXECUTION FUNCTIONS
# ---------------------------------------------------------
def run_launch_script():
    lock_buttons("INITIALIZING...")
    console_output.configure(state=tk.NORMAL)
    console_output.delete(1.0, tk.END)
    console_output.configure(state=tk.DISABLED)

    # Run the main() function from your gig_launcher.py in a background thread
    threading.Thread(
        target=execute_module, args=(gig_launcher.main,), daemon=True
    ).start()


def run_clear_script():
    lock_buttons("CLEARING...")
    console_output.configure(state=tk.NORMAL)
    console_output.delete(1.0, tk.END)
    console_output.configure(state=tk.DISABLED)

    # Run the main() function from your gig_close.py in a background thread
    threading.Thread(target=execute_module, args=(gig_close.main,), daemon=True).start()


def execute_module(target_function):
    """Executes the imported function and resets the UI when done."""
    try:
        # This will run your actual script logic!
        target_function()
    except Exception as e:
        print(f"\nSYSTEM ERROR: {e}")
    finally:
        root.after(0, unlock_buttons)


# ---------------------------------------------------------
# UI HELPERS
# ---------------------------------------------------------
def lock_buttons(status_text):
    btn_launch.config(state=tk.DISABLED, text=status_text, bg=BTN_BLUE_HOVER)
    btn_clear.config(state=tk.DISABLED, bg=BTN_GRAY_HOVER)


def unlock_buttons():
    btn_launch.config(state=tk.NORMAL, text="LAUNCH GIG RIG", bg=BTN_BLUE)
    btn_clear.config(state=tk.NORMAL, text="CLEAR DECK", bg=BTN_GRAY)
    print("\n--- SYSTEM READY ---")


# ==========================================
# Build the UI
# ==========================================
root = tk.Tk()
root.title("Gig Control Center")
root.iconbitmap(resource_path("icon.ico"))
# 1. Define your app's size
app_width = 800
app_height = 600

# 2. Ask Windows for the user's current screen resolution
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# 3. Calculate the exact center coordinates
x_coordinate = int((screen_width / 2) - (app_width / 2))
y_coordinate = int((screen_height / 2) - (app_height / 2))

# 4. Tell Tkinter the size AND the placement coordinates
root.geometry(f"{app_width}x{app_height}+{x_coordinate}+{y_coordinate}")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

btn_frame = tk.Frame(root, bg=BG_COLOR)
btn_frame.pack(pady=20, padx=20, fill=tk.X)

btn_clear = tk.Button(
    btn_frame,
    text="CLEAR DECK",
    font=("Segoe UI", 18, "bold"),
    bg=BTN_GRAY,
    fg="white",
    activebackground=BTN_GRAY_HOVER,
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    command=run_clear_script,
    width=20,
)
btn_clear.pack(side=tk.LEFT, fill=tk.Y)

btn_launch = tk.Button(
    btn_frame,
    text="LAUNCH GIG RIG",
    font=("Segoe UI", 24, "bold"),
    bg=BTN_BLUE,
    fg="white",
    activebackground=BTN_BLUE_HOVER,
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    command=run_launch_script,
)
btn_launch.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

console_output = scrolledtext.ScrolledText(
    root, bg=TEXT_BG, fg=TEXT_FG, font=("Consolas", 14), relief="flat", padx=10, pady=10
)
console_output.pack(padx=20, pady=(0, 20), fill=tk.BOTH, expand=True)

# --- THE MAGIC TRICK ---
# Hijack Python's print() statement and route it to our text box
sys.stdout = ConsoleRedirector(console_output)
sys.stderr = ConsoleRedirector(console_output)

print("System initialized. Awaiting command...\n")

root.mainloop()
