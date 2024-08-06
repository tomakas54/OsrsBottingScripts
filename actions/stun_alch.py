import time
import random
import threading
import keyboard
import pyautogui
import sys
import os
from humancursor import SystemCursor
from win32api import GetSystemMetrics

actions_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(actions_dir)

from logout import *

from actions.login import login
from utils.break_utils import *
from utils.window_utils import *
from utils.coordinates_utils import *
from utils.image_recognition_utils import *

pyautogui.FAILSAFE = False
# Define coordinates, sizes, and colors
relative_coords = {
    "inventory": (556, 240),
    "xp_drop": (450,76),
}
roi_sizes = {
    "inventory": (200, 250),
    "xp_drop": (60, 100),
}

colors = {
    "bank": [(255, 0, 255)],
    "xp_drop": [(255, 0, 0)]
}
template_image_paths = [f'assets/{i}.png' for i in range(1, 10)]
script_failed = False  # Initialize the script_failed variable
stop_event = threading.Event()  # Create a stop event for stopping the script

# Initialize counters for banking and crafting
stun_count = 0
alch_count = 0


def alch(cursor, alch_path, alch_item_path):
    """Finish crafting and interact with the bank."""
    global script_failed
    global alch_count
    screenshot_path = take_screenshot(hwnd)
    roi_inventory = (*relative_coords["inventory"], *roi_sizes["inventory"])
    alch_coords = template_match(screenshot_path, alch_path, threshold=0.8, roi=roi_inventory, scale_factor=0.5)
    if len(alch_coords) == 0:
        print("No alchemy coordinates found.")
        return
    click_coordinates(cursor, alch_coords[0])
    time.sleep(random.uniform(0.25, 0.5))
    screenshot_path = take_screenshot(hwnd)
    alch_item_coords = template_match(screenshot_path, alch_item_path, threshold=0.8, roi=roi_inventory, scale_factor=0.5)
    if len(alch_item_coords) == 0:
        print("No alchemy item coordinates found.")
        return
    click_coordinates(cursor, alch_item_coords[0])
    alch_count += 1

def stun(cursor, stun_path):
    """Finish crafting and interact with the bank."""
    global script_failed
    global stun_count
    time.sleep(random.uniform(0.1, 0.2))
    screenshot_path = take_screenshot(hwnd)
    roi_inventory = (*relative_coords["inventory"], *roi_sizes["inventory"])
    stun_coords = template_match(screenshot_path, stun_path, threshold=0.8, roi=roi_inventory, scale_factor=0.5)
    if len(stun_coords) == 0:
        print("No stun coordinates found.")
        return
    click_coordinates(cursor, stun_coords[0])
    time.sleep(random.uniform(0.25, 0.5))
    screenshot, window_left, window_top, window_width, window_height = get_window_screenshot(hwnd)
    npc_coords = find_color_coordinates(screenshot, colors["bank"], roi=(0, 0, window_width, window_height))
    if len(npc_coords) == 0:
        print("No NPC coordinates found.")
        return
    click_coordinates(cursor, pick_random_coordinate(npc_coords, window_left, window_top))
    stun_count += 1



def key_listener():
    """Listen for the 'q' key press to stop the script."""
    keyboard.wait('q')
    stop_event.set()
    print("Stop event set! Exiting...")
    
def stun_alch(stun_path, level_up_path,alch_path,alch_item_path):
    global script_failed
    global craft_count  # Declare the craft_count variable
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
    time.sleep(random.uniform(10, 20))
    PressButton('f3')
    try:
        # Start the key listener thread
        listener_thread = threading.Thread(target=key_listener)
        listener_thread.start()

        while time.time() < time_to_stop and not stop_event.is_set():
            screenshot, window_left, window_top, window_width, window_height = get_window_screenshot(hwnd)
            screenshot_path = take_screenshot(hwnd)        

            roi_xp_drop = (*relative_coords["xp_drop"], *roi_sizes["xp_drop"])

            xp_coords = find_color_coordinates(screenshot, colors["xp_drop"], roi=roi_xp_drop)
            level_up_coords = template_match(screenshot_path, level_up_path, threshold=0.8, scale_factor = 0.5)

            if xp_coords.size > 0:
                #print('XP FOUND')
                last_xp_drop_time = time.time()  # Reset the timer
                xp_found = True
            else:
                #print('XP NOT FOUND')
                xp_found = False 

            if time.time() - last_xp_drop_time > 360:  # 10 seconds as an example
                print("XP NOT FOUND FOR A WHILE STOPPING SCRIPT")
                script_failed = True  # Set the failure flag
                update_status_file(True)  # Update status file
                break
            if len(level_up_coords) > 0:
                print("LEVEL UP")
                stun(cursor,stun_path)

            #qstun(cursor,stun_path)
            alch(cursor,alch_path,alch_item_path)
            if random.random() < 0.01:  # 10% chance to take a break on each iteration
                hover_to = generate_random_absolute_coords(GetSystemMetrics(0), GetSystemMetrics(1))
                print("HOVERING TO A RANDOM SCREEN COORDS")
                cursor.move_to(hover_to)
                take_a_break(30, 60)
            time.sleep(0.5)
        logout(cursor)
        update_status_file(script_failed)  # Update status file
        print(script_failed)
        return script_failed
    except Exception as e:
        print(f"An error occurred: {e}")
        script_failed = True  # Set the failure flag if an exception occurs
        update_status_file(True)  # Update status file
        return script_failed
    finally:
        print(f"Total alch: {alch_count}")
        print(f"Total stuns: {stun_count}")

if __name__ == "__main__":
    stun_alch('assets/curse.png','assets/fletch_lvl.png','assets/alch.png','assets/longbow_note.png')
