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
hwnd = findWindow_runelite('GIMGrupiokas')
relative_coords = {
    "inventory": (556, 240),  # Example coordinates
}

roi_sizes = {
    "inventory": (180, 250),  # Example ROI size for inventory
}

colors = {
    "logout_button": [(131,31,29)]
}
def logout(cursor):
    screenshot, window_left, window_top, window_width, window_height = get_window_screenshot(hwnd)
    roi_inventory = (*relative_coords["inventory"], *roi_sizes["inventory"])
    time.sleep(3)
    PressButton('esc')
    time.sleep(3)
    PressButton('f12')
    time.sleep(random.uniform(0.5, 1.5))
    screenshot, window_left, window_top, window_width, window_height = get_window_screenshot(hwnd)
    logout_coords = find_color_coordinates(screenshot, colors["logout_button"], roi=roi_inventory)
    print(logout_coords)
    click_coordinates(cursor, pick_random_coordinate(logout_coords, window_left, window_top))


    

