import time
import random
import threading
import keyboard
import pyautogui
import sys
import os
from humancursor import SystemCursor
from win32api import GetSystemMetrics
from pyHM import mouse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import simpy.library.io as io
from simpy.library.global_vals import *

from actions.login import login
from utils.break_utils import *
from utils.window_utils import *
from utils.coordinates_utils import *
from utils.image_recognition_utils import *
from logout import *
pyautogui.FAILSAFE = False
# Define coordinates, sizes, and colors
relative_coords = {
    "inventory": (556, 240),
    "fishing": (12, 45),
    "xp_drop": (450,76),
}
roi_sizes = {
    "inventory": (180, 250),
    "fishing": (140, 100),
    "xp_drop": (60, 100),
}

colors = {
    "is_fishing": [(0, 255, 0)],
    "fish_spot": [(255, 0, 255)],
    "bank_items": [(0, 0, 255)],
    "xp_drop": [(255, 0, 0)]
}
template_image_paths = [f'assets/{i}.png' for i in range(1, 10)]
script_failed = False  # Initialize the script_failed variable
stop_event = threading.Event()  # Create a stop event for stopping the script

def handle_droping(cursor):
    screenshot_path = take_screenshot(hwnd)
    roi_inventory = (*relative_coords["inventory"], *roi_sizes["inventory"])
    
    # Detect fish coordinates
    fish_coords = template_match_multiple(
        screenshot_path,
        ['assets/leaping_salmon.png','assets/leaping_trout.png','assets/leaping_sturgeon.png'],
        threshold=0.8,
        roi=roi_inventory,
        scale_factor=0.5)
    
    # Sort coordinates first by y (row), then by x (column)
    fish_coords_sorted = sorted(fish_coords, key=lambda coord: (coord[1], coord[0]))
    print(fish_coords_sorted)
    
    # Simulate dropping items in the sorted order
    click_coordinates(cursor,fish_coords_sorted[0])
    for coord in fish_coords_sorted[1:]:
        io.wind_mouse(coord[0], coord[1], speed=0.2)
        Click('left')   


def handle_fishing(cursor):
    screenshot, window_left, window_top, window_width, window_height = get_window_screenshot(hwnd)
    screenshot_path = take_screenshot(hwnd) 
    fish_spot_coords = find_color_coordinates(screenshot, colors["fish_spot"], roi=(0, 0, window_width, window_height))
    roi_fishing = (*relative_coords["fishing"], *roi_sizes["fishing"])
    is_fishing_coords = find_color_coordinates(screenshot, colors["is_fishing"], roi=roi_fishing)
    if len(is_fishing_coords) > 0:
        is_fishing = True
    else:
        is_fishing = False

    if is_fishing:
        print('FISHING')
    else:
        print('NOT FISHING')
        full_inv_ano_coords = template_match(screenshot_path, 'assets/full_inv_fish.png', threshold=0.8)
        if len(full_inv_ano_coords) > 0:
            print('FULL INV')
            if random.random() < 0.5:  # 10% chance to take a break on each iteration
                take_a_break(5, 15)
            handle_droping(cursor=cursor)
        click_coordinates(cursor, pick_random_coordinate(fish_spot_coords, window_left, window_top))
        if random.random() < 0.8:  # 10% chance to take a break on each iteration
            hover_to = generate_random_absolute_coords(GetSystemMetrics(0), GetSystemMetrics(1))
            print("HOVERING TO A RANDOM SCREEN COORDS")
            cursor.move_to(hover_to)         
        time.sleep(random.uniform(10,12))
    global script_failed  # Declare global variable

def key_listener():
    """Listen for the 'q' key press to stop the script."""
    keyboard.wait('q')
    stop_event.set()
    print("Stop event set! Exiting...")
    
def fish():
    global script_failed
    name = get_account_name()
    if not name:
        print("Failed to retrieve account name. Exiting...")
        script_failed = True
        update_status_file(True)  # Update status file
        return script_failed
    
    hwnd = findWindow_runelite(name)
    
    cursor = SystemCursor()
    login(cursor, hwnd)
    action_done = False
    last_xp_drop_time = time.time()
    time_to_stop = generate_botting_time(2)

    try:
        # Start the key listener thread
        listener_thread = threading.Thread(target=key_listener)
        listener_thread.start()

        while time.time() < time_to_stop and not stop_event.is_set():
            screenshot, window_left, window_top, window_width, window_height = get_window_screenshot(hwnd)
            roi_xp_drop = (*relative_coords["xp_drop"], *roi_sizes["xp_drop"])
            xp_coords = find_color_coordinates(screenshot, colors["xp_drop"], roi=roi_xp_drop)


            if xp_coords.size > 0:
                print('XP FOUND')             
                last_xp_drop_time = time.time()  # Reset the timer
                xp_found = True
            else:
                print('XP NOT FOUND')
                xp_found = False

            if time.time() - last_xp_drop_time > 360:  # 10 seconds as an example
                print("XP NOT FOUND FOR A WHILE STOPPING SCRIPT")
                script_failed = True  # Set the failure flag
                update_status_file(True)  # Update status file
                break

            handle_fishing(cursor)
            time.sleep(0.5)
                    
        logout(cursor)
        update_status_file(script_failed)  # Update status file
        return script_failed
    except Exception as e:
        print(f"An error occurred: {e}")
        script_failed = True  # Set the failure flag if an exception occurs
        update_status_file(True)  # Update status file
        return script_failed

if __name__ == "__main__":
    fish()
