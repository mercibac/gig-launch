import pyautogui
from utils import resource_path
import time


icon_def = resource_path("assets/defender_activate_icon.png")


def click_on_img(img):
    try:
        icon_location = pyautogui.locateCenterOnScreen(img, confidence=0.8)

        if icon_location:
            print("Icon found! Clicking it...")
            pyautogui.click(icon_location)
            time.sleep(1)
        else:
            print("Could not find the icon on the screen.")

    except pyautogui.ImageNotFoundException:
        print("PyAutoGUI could not locate the image.")


def switch_defender(option):
    pyautogui.click()
    pyautogui.press("win")
    time.sleep(1)
    pyautogui.write("windows security", interval=0.1)

    time.sleep(0.5)

    pyautogui.press("enter")

    time.sleep(7)

    if option == "on":
        icon_def_1 = resource_path("assets/defender_activate_icon.png")
    if option == "off":
        icon_def_1 = resource_path("./assets/defender_protection_icon.png")
    icon_def_2 = resource_path("./assets/defender_settings_icon.png")
    click_on_img(icon_def_1)
    click_on_img(icon_def_2)

    icon_def_3 = resource_path("./assets/defender_realtime_icon.png")

    image_pos = pyautogui.locateCenterOnScreen(icon_def_3, confidence=0.9)

    if image_pos is not None:
        img_x, img_y = image_pos

        target_x = img_x - 20
        if option == "on":
            target_y = img_y + 160
        if option == "off":
            target_y = img_y + 130

        pyautogui.moveTo(target_x, target_y, duration=0.5)
        pyautogui.click()

        print(f"Success! Clicked 20px below the image at: ({target_x}, {target_y})")
    else:
        print("Error: Image could not be found on the screen.")

    time.sleep(3)
    pyautogui.hotkey("alt", "f4")
