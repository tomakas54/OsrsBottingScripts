import time
import random
import pyautogui
from humancursor import SystemCursor
from actions.login import login
from utils.break_utils import *
from utils.window_utils import *
from utils.coordinates_utils import *
from utils.image_recognition_utils import *
from logout import *


colors = {
    "next": [(0, 255, 0)], #GREEN
    "next_unavailable": [(200, 255, 0)],
    "other": [(255, 150, 0)],
    "stop": [(255, 0, 255)],
    "mark": [(255, 255, 0)],
    "xp_drop": [(255, 0, 0)]
}

relative_coords = {
    "screen": (0, 65),
    "xp_drop": (450,76),
}

roi_sizes = {
    "screen": (525, 400),
    "xp_drop": (60, 100),
}
script_failed = False # Initialize the script_failed variable
def run():
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
        while time.time() < time_to_stop:
            screenshot, window_left, window_top, window_width, window_height = get_window_screenshot(hwnd)
                    
            roi_screen = (*relative_coords["screen"], *roi_sizes["screen"])
            roi_xp_drop = (*relative_coords["xp_drop"], *roi_sizes["xp_drop"])

            next_obs_coords = find_color_coordinates(screenshot, colors["next"], roi=roi_screen)
            next_obs_unavailable_coords = find_color_coordinates(screenshot, colors["next_unavailable"], roi=roi_screen)
            stop_obs_coords = find_color_coordinates(screenshot, colors["stop"], roi=roi_screen)
            mark_coords = find_color_coordinates(screenshot, colors["mark"], roi=roi_screen)
            xp_coords = find_color_coordinates(screenshot, colors["xp_drop"], roi=roi_xp_drop)

            if xp_coords.size > 0:
                print('XP FOUND')
                last_xp_drop_time = time.time()  # Reset the timer
            else:
                print('XP NOT FOUND')

            if time.time() - last_xp_drop_time > 360:  # 10 seconds as an example
                print("XP NOT FOUND FOR A WHILE STOPPING SCRIPT")
                script_failed = True  # Set the failure flag
                update_status_file(True)  # Update status file
                break
            if next_obs_coords.size > 0 and action_done == False:
                click_coordinates(cursor, pick_random_coordinate(next_obs_coords, window_left, window_top))
                action_done = True
            elif mark_coords.size > 0:
                click_coordinates(cursor, pick_random_coordinate(mark_coords, window_left, window_top))
                action_done = False
                time.sleep(random.uniform(0.5, 1.5))
            else:
               if next_obs_unavailable_coords.size == 0:
                   print("RUNING")
               else:
                   print("CLIMBING")
                   time.sleep(random.uniform(1, 2))
                   action_done = False

               
                
                
        logout(cursor)
        update_status_file(script_failed)  # Update status file
        return script_failed
    except Exception as e:
        print(f"An error occurred: {e}")
        script_failed = True  # Set the failure flag if an exception occurs
        update_status_file(True)  # Update status file
        return script_failed

if __name__ == "__main__":
    run()