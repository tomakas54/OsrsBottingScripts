import time
import random
import threading
import keyboard
import sys
import os
from humancursor import SystemCursor
from win32api import GetSystemMetrics
from rich.console import Console
from rich.traceback import install
# Import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from simpy.library import io
from simpy.library.global_vals import *
from actions.login import login
from actions.bank import Bank
from utils import break_utils, window_utils, coordinates_utils, image_recognition_utils, hardware_inputs, constants
from logout import logout
import multiprocessing as mp
# Define coordinates, sizes, and colors
console = Console()
install()
template_image_paths = [f'assets/{i}.png' for i in range(1, 10)]
script_failed = False  # Initialize the script_failed variable
stop_event = threading.Event()  # Create a stop event for stopping the script

# Initialize counters for banking and crafting
bank_count = 0
craft_count = 0
no_xp_count = 0




class Craft1414Bot:
    def __init__(self, first_item_path, second_item_path):
        self.stop_event = threading.Event()
        self.cursor = SystemCursor()
        self.bank = Bank()
        self.coordinates_utils = coordinates_utils.Coordinates()
        self.image_recognition_utils = image_recognition_utils.ImageRecognition()
        
        self.first_item_path = first_item_path
        self.second_item_path = second_item_path
        
        self.script_failed = False
        self.last_xp_time = time.time()

    def handle_crafting(self) -> None:
        roi_inventory = (*constants.RELATIVE_COORDS["inventory"], *constants.ROI_SIZES["inventory"])
        first_item_coords = self.image_recognition_utils.generate_random_b_box_coord(
            self.image_recognition_utils.template_match(
                self.first_item_path,
                threshold=0.8,
                roi=roi_inventory,
                scaling_factor=0.5
            )
        )
        
        if first_item_coords and len(first_item_coords) > 0:
            first_item_index = random.randint(0, len(first_item_coords) - 1)
            console.log(f"Clicking on first item: {first_item_coords[first_item_index]}")
            self.coordinates_utils.click_coordinates(first_item_coords[first_item_index])
        else:
            window_utils.update_status_file(True)
            return

        second_item_coords = self.image_recognition_utils.generate_random_b_box_coord(
            self.image_recognition_utils.template_match(
                self.second_item_path,
                threshold=0.8,
                roi=roi_inventory,
                scaling_factor=0.5
            )
        )

        if second_item_coords and len(second_item_coords) > 0:
            second_item_index = random.randint(0, len(second_item_coords) - 1)
            console.log(f"Clicking on second item: {second_item_coords[second_item_index]}")
            self.coordinates_utils.click_coordinates(second_item_coords[second_item_index])
            time.sleep(random.uniform(0.5, 1.5))
            hardware_inputs.PressButton('space')
        else:
            window_utils.update_status_file(True)
            return
        
        while len(first_item_coords) > 0:
            first_item_coords = self.image_recognition_utils.generate_random_b_box_coord(
                self.image_recognition_utils.template_match(
                    self.first_item_path,
                    threshold=0.8,
                    roi=roi_inventory,
                    scaling_factor=0.5
                )
            )
        return
        
        
    def bank_items(self) -> None:
        global script_failed  # Declare global variable
        global bank_count  # Declare the bank_count variable

        roi_inventory = (*constants.RELATIVE_COORDS["inventory"], *constants.ROI_SIZES["inventory"])
        first_item_coords = self.image_recognition_utils.generate_random_b_box_coord(
            self.image_recognition_utils.template_match(
                self.first_item_path,
                threshold=0.8,
                roi=roi_inventory,
                scaling_factor=0.5
            )
        )        
        second_item_coords = self.image_recognition_utils.generate_random_b_box_coord(
            self.image_recognition_utils.template_match(
                self.second_item_path,
                threshold=0.8,
                roi=roi_inventory,
                scaling_factor=0.5
            )
        )
        
        if first_item_coords and len(first_item_coords) == 0 and second_item_coords and len(second_item_coords) == 0:
            return
        
        bank_attempts = 0  # Initialize the no materials counter
        while bank_attempts < 3:
            self.bank.bank_inventory()
            is_first_item = self.bank.take_item(self.first_item_path)
            is_second_item = self.bank.take_item(self.second_item_path)               
            
            if not is_first_item and not is_second_item:
                time.sleep(random.uniform(0.1, 1.5))
                hardware_inputs.PressButton('esc')
                bank_count += 1
                return  # Exit the function successfully
            else:
                bank_attempts += 1

        console.log("No bank found after 3 attempts. Quitting script.")
        script_failed = True
        window_utils.update_status_file(True)  # Update status file
        

              
    def make_item(self) -> bool:      
        time_to_stop = break_utils.generate_botting_time(min_time=2)
        login() 
        try:            
            self.bank.set_quantity(14)
            while time.time() < time_to_stop and not self.stop_event.is_set():             
                if time.time() - self.last_xp_time > 180:
                    console.log("No XP detected for 3 minutes. Stopping script.")
                    self.script_failed = True
                    break
                self.bank_items()
                self.handle_crafting()
                if len(self.image_recognition_utils.template_match('assets/Congrats_flag.png')) > 0:
                    self.bank_items()
                if self.coordinates_utils.xp_check():
                    console.log("XP drop found in this iteration.")
                    self.last_xp_time = time.time()  
                                  
                if random.random() < 0.5:
                    break_utils.take_a_break(5, 15)

        except Exception as e:
            console.log(f"An error occurred: {e}")
            self.script_failed = True
        finally:
            window_utils.update_status_file(self.script_failed)

        return self.script_failed

if __name__ == "__main__":
    bot = Craft1414Bot('assets/bow_u.png', 'assets/bow_string.png')
    bot.make_item()