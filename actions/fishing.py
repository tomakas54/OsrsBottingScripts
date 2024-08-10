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
from actions.camera import rotate_camera_till_color,calibrate_camera_rotation,calibrate_camera_zoom
from utils import break_utils, window_utils, coordinates_utils, image_recognition_utils,hardware_inputs,constants
from logout import logout


# Constants

class FishingBot:
    def __init__(self):
        self.script_failed = False
        self.stop_event = threading.Event()
        self.cursor = SystemCursor()
        self.hwnd = None
        self.last_xp_drop_time = time.time()

    @staticmethod
    @lru_cache(maxsize=None)
    def distance_from_center(coord : list) -> float:
        #COORDS ARE INVERTED!!!
        x, y = coord
        return ((y - 380)**2 + (x - 280)**2)**0.5

    def handle_dropping(self) -> None:
        _,_,_,_,_,screenshot_path = window_utils.get_window_screenshot(self.hwnd)
        roi_inventory = (*constants.RELATIVE_COORDS["inventory"], *constants.ROI_SIZES["inventory"])
        fish_coords = image_recognition_utils.generate_random_b_box_coord(
            image_recognition_utils.template_match_multiple(
                screenshot_path,
                ['assets/leaping_salmon.png', 'assets/leaping_trout.png', 'assets/leaping_sturgeon.png'],
                threshold=0.8,
                roi=roi_inventory,
                scaling_factor=0.5
        ))
        fish_coords_sorted = sorted(fish_coords, key=lambda coord: (coord[1], coord[0]))
        if fish_coords_sorted:
            coordinates_utils.click_coordinates(self.cursor, fish_coords_sorted[0])
            for coord in fish_coords_sorted[1:]:
                io.wind_mouse(coord[0], coord[1], speed=0.2)
                hardware_inputs.Click('left')

    def handle_fishing(self) -> None:
        screenshot, window_left, window_top, window_width, window_height,screenshot_path = window_utils.get_window_screenshot(self.hwnd)
        is_fishing = coordinates_utils.action_check(screenshot)

        if not is_fishing:
            time.sleep(random.uniform(2.5, 3.5))
            _,_,_,_,_,screenshot_path = window_utils.get_window_screenshot(self.hwnd)
            if image_recognition_utils.generate_random_b_box_coord(
                    image_recognition_utils.template_match(
                        screenshot_path, 
                        'assets/full_inv_fish.png', 
                        threshold=0.8)
                ):
                print('FULL INV')
                if random.random() < 0.5:
                    break_utils.take_a_break(5, 15)
                self.handle_dropping()
            fish_spot_coords = tuple(coordinates_utils.find_color_coordinates(screenshot, constants.COLORS["pink"], roi=(0, 0, window_width, window_height)))
            fish_spot_coords = [tuple(coord) if isinstance(coord, np.ndarray) else coord for coord in fish_spot_coords]
            fish_spot_coords = sorted(fish_spot_coords, key=self.distance_from_center)[:50]
            if len(fish_spot_coords) > 0:
                coordinates_utils.click_coordinates(self.cursor, coordinates_utils.pick_random_coordinate(fish_spot_coords,window_left,window_top))
            else:
                rotate_camera_till_color(constants.COLORS['pink'],self.hwnd)    

            if random.random() < 0.8:
                hover_to = coordinates_utils.generate_random_absolute_coords(GetSystemMetrics(0), GetSystemMetrics(1))
                print("HOVERING TO A RANDOM SCREEN COORDS")
                self.cursor.move_to(hover_to)
            
            time.sleep(random.uniform(10, 12))

    def key_listener(self) -> None:
        keyboard.wait('q')
        self.stop_event.set()
        print("Stop event set! Exiting...")

    def fish(self) -> bool:
        name = window_utils.get_account_name()
        if not name:
            print("Failed to retrieve account name. Exiting...")
            self.script_failed = True
            window_utils.update_status_file(True)
            return self.script_failed

        self.hwnd = window_utils.findWindow_runelite(name)
        login(self.cursor, self.hwnd)
        time_to_stop = break_utils.generate_botting_time(min_time = 2)

        listener_thread = threading.Thread(target=self.key_listener)
        listener_thread.start()
        calibrate_camera_rotation('west')
        calibrate_camera_zoom(20,'down')
        try:
            while time.time() < time_to_stop and not self.stop_event.is_set():
                screenshot, _, _, _, _ , _= window_utils.get_window_screenshot(self.hwnd)
                if coordinates_utils.xp_check(screenshot):
                    self.last_xp_drop_time = time.time()
                if time.time() - self.last_xp_drop_time > 360:
                    print("XP NOT FOUND FOR A WHILE STOPPING SCRIPT")
                    self.script_failed = True
                    window_utils.update_status_file(True)
                    break
                self.handle_fishing()
                time.sleep(0.5)

        except Exception as e:
            print(f"An error occurred: {e}")
            self.script_failed = True
        finally:
            logout(self.cursor,self.hwnd)
            window_utils.update_status_file(self.script_failed)

        return self.script_failed

if __name__ == "__main__":
    bot = FishingBot()
    bot.fish()