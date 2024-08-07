import time
import random
import threading
import keyboard
import pyautogui
import sys
import os
from humancursor import SystemCursor
from win32api import GetSystemMetrics

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
    "bank": (350, 280),
    "xp_drop": (450,76),
}
roi_sizes = {
    "inventory": (180, 250),
    "bank_items": (140, 79),
    "xp_drop": (60, 100),
}

colors = {
    "first_item": [(0, 255, 255)],
    "second_item": [(255, 255, 255)],
    "bank": [(255, 0, 255)],
    "bank_items": [(0, 0, 255)],
    "xp_drop": [(255, 0, 0)]
}
template_image_paths = [f'assets/{i}.png' for i in range(1, 10)]
script_failed = False  # Initialize the script_failed variable
stop_event = threading.Event()  # Create a stop event for stopping the script

# Initialize counters for banking and crafting
bank_count = 0
craft_count = 0
no_xp_count = 0

def handle_crafting(cursor, first_item_coords, second_item_coords):
    """Perform crafting action based on item coordinates."""
    if first_item_coords:
        print(f"Clicking on first item: {first_item_coords}")
        click_coordinates(cursor, first_item_coords)
    else:
        return
    
    if second_item_coords:
        print(f"Clicking on second item: {second_item_coords}")
        click_coordinates(cursor, second_item_coords)
        time.sleep(random.uniform(0.5, 1.5))
        PressButton('space')
    else:
        return

def bank_items(cursor, bank_coords, bank_items_coords, first_item_path, second_item_path, window_left, window_top, template_image_paths):
    """Finish crafting and interact with the bank."""
    global script_failed  # Declare global variable
    global bank_count  # Declare the bank_count variable
    print("BANKING")
    
    no_materials_attempts = 0  # Initialize the no materials counter

    while no_materials_attempts < 3:
        if bank_coords.size > 0:
            click_coordinates(cursor, pick_random_coordinate(bank_coords, window_left, window_top))
            click_coordinates(cursor, pick_random_coordinate(bank_items_coords, window_left, window_top))
            time.sleep(random.uniform(0.6, 0.7))
            screenshot_path = take_screenshot(hwnd)
            matches_quantity = template_match_digits(screenshot_path, template_image_paths, roi=(358, 285, 90, 35), threshold=0.9)
            
            if len(matches_quantity) >= 2:
                first_item_bank_coords = template_match(screenshot_path, first_item_path, threshold=0.8, scale_factor=0.5)
                second_item_bank_coords = template_match(screenshot_path, second_item_path, threshold=0.8, scale_factor=0.5)
                
                if first_item_bank_coords and second_item_bank_coords:
                    click_coordinates(cursor, first_item_bank_coords[0])
                    click_coordinates(cursor, second_item_bank_coords[0])
                    time.sleep(random.uniform(0.1, 1.5))
                    
                    PressButton('esc')
                    bank_count += 1  # Increment bank counter
                    return  # Exit the function successfully
                else:
                    print("No items found in the bank! Terminating script...")
                    script_failed = True
                    update_status_file(True)  # Update status file
                    return  # Exit the function early
            else:
                print(f"No materials left! Attempt {no_materials_attempts + 1} of 3")
                no_materials_attempts += 1
        else:
            print("BANK NOT FOUND")
            return  # Exit the function early if the bank is not found

    print("No materials found after 3 attempts. Quitting script.")
    script_failed = True
    update_status_file(True)  # Update status file


def key_listener():
    """Listen for the 'q' key press to stop the script."""
    keyboard.wait('q')
    stop_event.set()
    print("Stop event set! Exiting...")
    
def make_item(first_item_path, second_item_path, level_up_path):
    global script_failed
    global craft_count  # Declare the craft_count variable
    global no_xp_count
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
            screenshot_path = take_screenshot(hwnd)        
            roi_inventory = (*relative_coords["inventory"], *roi_sizes["inventory"])
            roi_bank_items = (*relative_coords["bank"], *roi_sizes["bank_items"])
            roi_xp_drop = (*relative_coords["xp_drop"], *roi_sizes["xp_drop"])

            first_item_coords = template_match(screenshot_path, first_item_path, threshold=0.8, roi=roi_inventory, scale_factor = 0.3)
            second_item_coords = template_match(screenshot_path, second_item_path, threshold=0.8, roi=roi_inventory, scale_factor = 0.3)
            bank_coords = find_color_coordinates(screenshot, colors["bank"], roi=(0, 0, window_width, window_height))
            bank_items_coords = find_color_coordinates(screenshot, colors["bank_items"], roi=roi_bank_items)
            xp_coords = find_color_coordinates(screenshot, colors["xp_drop"], roi=roi_xp_drop)
            level_up_coords = template_match(screenshot_path, level_up_path, threshold=0.8, scale_factor = 0.5)

            if xp_coords.size > 0:
                #print('XP FOUND')
                
                last_xp_drop_time = time.time()  # Reset the timer
                no_xp_count = 0
                xp_found = True
            else:
                #print('XP NOT FOUND')
                no_xp_count += 1
                xp_found = False

            if no_xp_count > 0 and no_xp_count % 100 == 0:
                bank_items(
                    cursor, bank_coords, bank_items_coords,
                    first_item_path, second_item_path,
                    window_left, window_top, template_image_paths
                )
                action_done = False        
            if bank_count == 0:
                click_coordinates(cursor, pick_random_coordinate(bank_coords, window_left, window_top))
                time.sleep(random.uniform(0.5, 1))    
                pyautogui.write('2002', interval=random.uniform(0.1, 0.2)) 

            if time.time() - last_xp_drop_time > 360:  # 10 seconds as an example
                print("XP NOT FOUND FOR A WHILE STOPPING SCRIPT")
                script_failed = True  # Set the failure flag
                update_status_file(True)  # Update status file
                break

            if len(level_up_coords) > 0:
                print("LEVEL UP")
                bank_items(
                    cursor, bank_coords, bank_items_coords,
                    first_item_path, second_item_path,
                    window_left, window_top, template_image_paths
                )
                action_done = False

            if len(second_item_coords) == 0:
                print('first item:' + str(len(first_item_coords)))
                print('second item:' + str(len(second_item_coords)))
                bank_items(
                    cursor, bank_coords, bank_items_coords,
                    first_item_path, second_item_path,
                    window_left, window_top, template_image_paths
                )
                action_done = False
                if script_failed:
                    break
                time.sleep(random.uniform(0.5, 1.5))
            else:
                if not action_done:
                    index_1 = random.randint(0, len(first_item_coords)-1)
                    index_2 = random.randint(0, len(second_item_coords)-1)
                    handle_crafting(
                        cursor, first_item_coords[index_1],
                        second_item_coords[index_2]
                    )
                    craft_count += 1  # Increment craft counter
                    action_done = True                   
                    if random.random() < 0.5:
                        hover_to = generate_random_absolute_coords(GetSystemMetrics(0), GetSystemMetrics(1))
                        print("HOVERING TO A RANDOM SCREEN COORDS")
                        cursor.move_to(hover_to)
                        
                    if random.random() < 0.1:  # 10% chance to take a break on each iteration
                        take_a_break(30, 60)
                    time.sleep(random.uniform(0.5, 1.5))
                    
        logout(cursor)
        update_status_file(script_failed)  # Update status file
        return script_failed
    except Exception as e:
        print(f"An error occurred: {e}")
        script_failed = True  # Set the failure flag if an exception occurs
        update_status_file(True)  # Update status file
        return script_failed
    finally:
        print(f"Total banks: {bank_count}")
        print(f"Total crafts: {craft_count}")

if __name__ == "__main__":
    make_item('assets/bow_u.png', 'assets/bow_string.png', 'assets/Congrats_flag.png')
