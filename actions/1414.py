import time
import random
import threading
import keyboard
import sys
import os
import numpy as np
from functools import lru_cache
from humancursor import SystemCursor
from win32api import GetSystemMetrics

# Import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from simpy.library import io
from simpy.library.global_vals import *
from actions.login import login
from actions.camera import calibrate_camera
from actions.bank import bank_inventory,take_item,set_quantity,enter_pin
from utils import break_utils, window_utils, coordinates_utils, image_recognition_utils,hardware_inputs
from logout import logout
# Define coordinates, sizes, and colors
RELATIVE_COORDS = {
    "inventory": (556, 240),
    "bank": (350, 280),
    "xp_drop": (450,76),
}
ROI_SIZES = {
    "inventory": (180, 250),
    "bank_items": (140, 79),
    "xp_drop": (60, 100),
}

COLORS = {
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

class Craft1414Bot:
    def __init__(self,first_item_path,second_item_path):
        self.script_failed = False
        self.stop_event = threading.Event()
        self.cursor = SystemCursor()
        self.hwnd = None
        self.last_xp_drop_time = time.time()
        self.first_item_path = first_item_path
        self.second_item_path = second_item_path

    def handle_crafting(self) -> str:
        """Perform crafting action based on item coordinates."""
        screenshot_path = window_utils.take_screenshot(self.hwnd)
        roi_inventory = (*RELATIVE_COORDS["inventory"], *ROI_SIZES["inventory"])
        first_item_coords = image_recognition_utils.generate_random_b_box_coord(
            image_recognition_utils.template_match(
                screenshot_path,
                self.first_item_path,
                threshold=0.8,
                roi=roi_inventory,
                scaling_factor=0.5
        ))
        second_item_coords = image_recognition_utils.generate_random_b_box_coord(
            image_recognition_utils.template_match(
                screenshot_path,
                self.second_item_path,
                threshold=0.8,
                roi=roi_inventory,
                scaling_factor=0.5
        ))
        first_item_index = random.randint(0, 13)
        second_item_index = random.randint(0, 13)
        rand_int = random.randint(1,2)
        
        if first_item_coords:
            print(f"Clicking on first item: {first_item_coords[first_item_index]}")
            coordinates_utils.click_coordinates(self.cursor, first_item_coords[first_item_index])
        else:
            window_utils.update_status_file(True)
            return
        
        if second_item_coords:
            print(f"Clicking on second item: {second_item_coords[second_item_index]}")
            coordinates_utils.click_coordinates(self.cursor, second_item_coords[second_item_index])
            time.sleep(random.uniform(0.5, 1.5))
            hardware_inputs.PressButton('space')
        else:
            window_utils.update_status_file(True)  
            return
        if random.random() < 0.8:
            hover_to = coordinates_utils.generate_random_absolute_coords(GetSystemMetrics(0), GetSystemMetrics(1))
            print("HOVERING TO A RANDOM SCREEN COORDS")
            self.cursor.move_to(hover_to)
        while len(first_item_coords) > 0:
            screenshot_path = window_utils.take_screenshot(self.hwnd)
            first_item_coords = image_recognition_utils.generate_random_b_box_coord(
            image_recognition_utils.template_match(
                screenshot_path,
                self.first_item_path,
                threshold=0.8,
                roi=roi_inventory,
                scaling_factor=0.5
            ))
            print('CRAFTING!')
            time.sleep(0.5)
        return

        

    def bank_items(self):
        """Finish crafting and interact with the bank."""
        global script_failed  # Declare global variable
        global bank_count  # Declare the bank_count variable
        screenshot_path = window_utils.take_screenshot(self.hwnd)
        roi_inventory = (*RELATIVE_COORDS["inventory"], *ROI_SIZES["inventory"])
        first_item_coords = image_recognition_utils.generate_random_b_box_coord(
            image_recognition_utils.template_match(
                screenshot_path,
                self.first_item_path,
                threshold=0.8,
                roi=roi_inventory,
                scaling_factor=0.5
        ))
        second_item_coords = image_recognition_utils.generate_random_b_box_coord(
            image_recognition_utils.template_match(
                screenshot_path,
                self.second_item_path,
                threshold=0.8,
                roi=roi_inventory,
                scaling_factor=0.5
        ))
        if len(first_item_coords) > 0 and len(second_item_coords) > 0:
            return
        bank_attempts = 0  # Initialize the no materials counter
        while bank_attempts < 3:              
                bank_inventory(self.hwnd,self.cursor)
                is_first_item = take_item(self.hwnd,self.cursor,self.first_item_path)
                is_second_item = take_item(self.hwnd,self.cursor,self.second_item_path)               
                if not is_first_item and not is_second_item:
                    time.sleep(random.uniform(0.1, 1.5))
                    hardware_inputs.PressButton('esc')
                    bank_count += 1
                    return  # Exit the function successfully
                else:
                    bank_attempts += 1


        print("No bank found after 3 attempts. Quitting script.")
        script_failed = True
        window_utils.update_status_file(True)  # Update status file


    def key_listener(self) -> None:
        keyboard.wait('q')
        self.stop_event.set()
        print("Stop event set! Exiting...")
    
    def make_item(self) -> bool:
        name = window_utils.get_account_name()
        if not name:
            print("Failed to retrieve account name. Exiting...")
            self.script_failed = True
            window_utils.update_status_file(True)
            return self.script_failed

        self.hwnd = window_utils.findWindow_runelite(name)
        login(self.cursor, self.hwnd)
        time_to_stop = break_utils.generate_botting_time(2)

        listener_thread = threading.Thread(target=self.key_listener)
        listener_thread.start()
        #calibrate_camera('west')
        #set_quantity(self.hwnd,14,self.cursor)
        try:
            while time.time() < time_to_stop and not self.stop_event.is_set():
                screenshot, _, _, _, _ = window_utils.get_window_screenshot(self.hwnd)
                if coordinates_utils.xp_check(screenshot):
                    print('XP FOUND')
                    self.last_xp_drop_time = time.time()
                if time.time() - self.last_xp_drop_time > 360:
                    print("XP NOT FOUND FOR A WHILE STOPPING SCRIPT")
                    self.script_failed = True
                    window_utils.update_status_file(True)
                    break
                self.bank_items()
                self.handle_crafting()
                if random.random() < 0.5:
                    break_utils.take_a_break(5, 15)

        except Exception as e:
            print(f"An error occurred: {e}")
            self.script_failed = True
        finally:
            '''logout(self.cursor,self.hwnd)'''
            window_utils.update_status_file(self.script_failed)

        return self.script_failed

if __name__ == "__main__":
    bot = Craft1414Bot('assets/bow_u.png','assets/bow_string.png')
    bot.make_item()
