import pyautogui
import numpy as np
import random
from humancursor import SystemCursor
import time
import threading
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.break_utils import *
from utils.window_utils import *
from utils.coordinates_utils import *

RELATIVE_COORDS = {
    "inventory": (556, 240),  # Example coordinates
}

ROI_SIZES = {
    "inventory": (180, 250),  # Example ROI size for inventory
}

COLORS = {
    "logout_button": [(131,31,29)]
}
def logout(cursor,hwnd : int) -> None:
    screenshot, window_left, window_top, _, _ = get_window_screenshot(hwnd)
    roi_inventory = (*RELATIVE_COORDS["inventory"], *ROI_SIZES["inventory"])
    time.sleep(random.uniform(3,5))
    PressButton('esc')
    time.sleep(random.uniform(3,5))
    PressButton('f12')
    time.sleep(random.uniform(1, 1.5))
    screenshot, window_left, window_top, _, _ = get_window_screenshot(hwnd)
    logout_coords = find_color_coordinates(screenshot, COLORS["logout_button"], roi=roi_inventory)
    print(logout_coords)
    click_coordinates(cursor, pick_random_coordinate(logout_coords, window_left, window_top))


    

