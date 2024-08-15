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
from rich.console import Console
from rich.traceback import install
# Import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from simpy.library import io
from simpy.library.global_vals import *
from actions.login import login
from camera import Camera
from utils import break_utils, window_utils, coordinates_utils, image_recognition_utils,hardware_inputs,constants
from logout import logout

console = Console()
install()

# Constants

class FishingBot:
    def __init__(self):
        self.script_failed = False
        self.stop_event = threading.Event()
        self.cursor = SystemCursor()
        self.hwnd = None
        self.last_xp_drop_time = time.time()
        self.image_recognition_utils = image_recognition_utils.ImageRecognition()
        self.coordinates_utils = coordinates_utils.Coordinates()
        self.camera = Camera()

    @staticmethod
    @lru_cache(maxsize=None)
    def distance_from_center(coord : list) -> float:
        #COORDS ARE INVERTED!!!
        x, y = coord
        return ((y - 380)**2 + (x - 280)**2)**0.5

    def handle_dropping(self) -> None:
        roi_inventory = (*constants.RELATIVE_COORDS["inventory"], *constants.ROI_SIZES["inventory"])
        fish_coords = self.image_recognition_utils.generate_random_b_box_coord(
            self.image_recognition_utils.template_match_multiple(
                ['assets/leaping_salmon.png', 'assets/leaping_trout.png', 'assets/leaping_sturgeon.png'],
                threshold=0.8,
                roi=roi_inventory,
                scaling_factor=0.5
        ))
        fish_coords_sorted = sorted(fish_coords, key=lambda coord: (coord[1], coord[0]))
        if fish_coords_sorted:
            self.coordinates_utils.click_coordinates(fish_coords_sorted[0])
            for coord in fish_coords_sorted[1:]:
                io.wind_mouse(coord[0], coord[1], speed=0.2)
                hardware_inputs.Click('left')

    def handle_fishing(self) -> None:
        is_fishing = self.coordinates_utils.action_check()
        
        if not is_fishing:
            time.sleep(random.uniform(2.5, 3.5))
            if self.image_recognition_utils.generate_random_b_box_coord(
                    self.image_recognition_utils.template_match(
                        'assets/full_inv_fish.png', 
                        threshold=0.8)
                ):
                console.log('FULL INV')
                if random.random() < 0.5:
                    break_utils.take_a_break(5, 15)
                self.handle_dropping()
            fish_spot_coords = tuple(self.coordinates_utils.find_color_coordinates(constants.COLORS["pink"]))
            fish_spot_coords = [tuple(coord) if isinstance(coord, np.ndarray) else coord for coord in fish_spot_coords]
            fish_spot_coords = sorted(fish_spot_coords, key=self.distance_from_center)[:50]
            if len(fish_spot_coords) > 0:
                self.coordinates_utils.click_coordinates(self.coordinates_utils.pick_random_coordinate(fish_spot_coords))
            else:
                self.camera.rotate_camera_till_color(constants.COLORS['pink'],self.hwnd)    

            if random.random() < 0.8:
                hover_to = self.coordinates_utils.generate_random_absolute_coords(GetSystemMetrics(0), GetSystemMetrics(1))
                console.log("HOVERING TO A RANDOM SCREEN COORDS")
                self.cursor.move_to(hover_to)
            
            time.sleep(random.uniform(10, 12))

    def fish(self) -> bool:

        name = window_utils.get_account_name()
        if not name:
            console.log("Failed to retrieve account name. Exiting...")
            self.script_failed = True
            window_utils.update_status_file(True)
            return self.script_failed

        login()
        time_to_stop = break_utils.generate_botting_time(min_time = 2)

        self.camera.calibrate_camera_rotation('west')
        self.camera.calibrate_camera_zoom(20,'down')
        try:
            while time.time() < time_to_stop and not self.stop_event.is_set():
                self.handle_fishing()
                time.sleep(0.5)

        except Exception as e:
            console.log(f"An error occurred: {e}")
            self.script_failed = True
        finally:
            #logout(self.cursor,self.hwnd)
            window_utils.update_status_file(self.script_failed)

        return self.script_failed

if __name__ == "__main__":
    bot = FishingBot()
    bot.fish()