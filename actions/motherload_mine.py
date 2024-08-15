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
from utils import break_utils, window_utils, coordinates_utils, image_recognition_utils,hardware_inputs,constants,walker_utils
from logout import logout
from osrs_walker import walk_to_coordinates,is_in_area
from camera import calibrate_camera_rotation





class FishingBot:
    def __init__(self):
        self.script_failed = False
        self.stop_event = threading.Event()
        self.cursor = SystemCursor()
        self.hwnd = None
        self.last_xp_drop_time = time.time()
        self.all_areas = walker_utils.generate_multiple_areas(constants.AREAS)

    @staticmethod
    @lru_cache(maxsize=None)
    def distance_from_center(coord : list) -> float:
        #COORDS ARE INVERTED!!!
        x, y = coord
        return ((x - 380)**2 + (y - 280)**2)**0.5
    
    def handle_ores(self,full_sack) -> None:
        print(self.all_areas)
        put_ores_loc_coord = self.all_areas['put_ores']
        print('PUTTING ORES')
        put_ores_loc_coord = random.choice(put_ores_loc_coord)
        walk_to_coordinates(([(put_ores_loc_coord[0], put_ores_loc_coord[1])]))
        time.sleep(1)
        screenshot, window_left, window_top, _, _, _ = window_utils.get_window_screenshot(self.hwnd)            
        hopper_coord = coordinates_utils.pick_random_coordinate(coordinates_utils.find_color_coordinates(screenshot,constants.COLORS["blue"]),window_top,window_left)
        coordinates_utils.click_coordinates(self.cursor,hopper_coord)
        time.sleep(random.uniform(3,6))
        if not full_sack:
            print('PUTTING ORES')
            put_ores_loc_coord = self.all_areas['put_ores']
            put_ores_loc_coord = random.choice(put_ores_loc_coord)
            walk_to_coordinates(([(put_ores_loc_coord[0], put_ores_loc_coord[1])]))
            time.sleep(1)
        if full_sack:
            time.sleep(random.uniform(3,7))
            _,_,_,_,_,screenshot_path = window_utils.get_window_screenshot(self.hwnd)
            hardware_inputs.PressButton('space')
            calibrate_camera_rotation('south')
            while len(image_recognition_utils.template_match(screenshot_path,'assets/sack_0.png')) == 0:
                _,_,_,_,_,screenshot_path = window_utils.get_window_screenshot(self.hwnd)                
                print("BANKING")
                screenshot, window_left, window_top, _, _, _ = window_utils.get_window_screenshot(self.hwnd)
                sack_coord = coordinates_utils.pick_random_coordinate(coordinates_utils.find_color_coordinates(screenshot,constants.COLORS["lightblue"]),window_top+5,window_left)
                coordinates_utils.click_coordinates(self.cursor,sack_coord)
                time.sleep(random.uniform(6,8))
                screenshot, window_left, window_top, _, _, _ = window_utils.get_window_screenshot(self.hwnd)
                bank_coord = coordinates_utils.pick_random_coordinate(coordinates_utils.find_color_coordinates(screenshot,constants.COLORS["pink"]),window_top+5,window_left)
                coordinates_utils.click_coordinates(self.cursor,bank_coord)
                time.sleep(random.uniform(3,5))
                screenshot, window_left, window_top, _, _, screenshot_path = window_utils.get_window_screenshot(self.hwnd)
                bank_items_coord = image_recognition_utils.generate_random_b_box_coord(image_recognition_utils.template_match(screenshot_path,'assets/bank_items.png',scaling_factor=0.5))
                coordinates_utils.click_coordinates(bank_items_coord)
                time.sleep(random.uniform(0.25,0.5))
                hardware_inputs.PressButton('esc')


            

    def handle_mining(self) -> None:
        screenshot, _, _, _, _, screenshot_path = window_utils.get_window_screenshot(self.hwnd)
        
        roi_sack_info = (*constants.RELATIVE_COORDS["sack_info"],*constants.ROI_SIZES["sack_info"])    
        is_sack_coords = coordinates_utils.find_color_coordinates(screenshot, constants.COLORS['red'], roi=roi_sack_info)
        
        is_mining = coordinates_utils.action_check(screenshot)
        print('MINING' if is_mining else 'MINING')
        is_sack = len(is_sack_coords) > 0
        print(is_sack)
        if not is_mining:
            _,_,_,_,_,screenshot_path = window_utils.get_window_screenshot(self.hwnd)
            if is_sack:
               self.handle_ores(is_sack) 
            if image_recognition_utils.template_match(screenshot_path, 'assets/motherload_fullinv.png', threshold=0.8):
                print('FULL INV')
                if random.random() < 0.5:
                    break_utils.take_a_break(5, 15)
                self.handle_ores(is_sack)
            if is_in_area(self.all_areas['mine']):                        
                mining_spots = image_recognition_utils.generate_random_b_box_coord(
                    image_recognition_utils.template_match(
                        screenshot_path,
                        'assets/mine_logo2.png',
                        threshold=0.5,
                        scaling_factor=0.3
                        ))
                mining_spots = [tuple(coord) if isinstance(coord, np.ndarray) else coord for coord in mining_spots]
                mining_spots = sorted(mining_spots, key=self.distance_from_center)[:1]
                matches_fix_spots = image_recognition_utils.template_match(screenshot_path,'assets/motherload_hammer.png',threshold=0.6)
                print(mining_spots)
                coordinates_utils.click_coordinates(self.cursor,mining_spots[0])
                time.sleep(random.uniform(5,10))
                _,_,_,_,_,screenshot_path = window_utils.get_window_screenshot(self.hwnd)
                if len(matches_fix_spots) == 2:
                    print('NEEDS FIXING')
            else:
                print('NOT AREA')
                mine_area = random.choice(self.all_areas['mine'])
                walk_to_coordinates(([(mine_area[0], mine_area[1])]))

            

    def key_listener(self) -> None:
        keyboard.wait('q')
        self.stop_event.set()
        print("Stop event set! Exiting...")

    def mine(self) -> bool:
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
        try:
            while time.time() < time_to_stop and not self.stop_event.is_set():
                screenshot, _, _, _, _, _ = window_utils.get_window_screenshot(self.hwnd)
                if coordinates_utils.xp_check(screenshot):
                    print('XP FOUND')
                    self.last_xp_drop_time = time.time()
                if time.time() - self.last_xp_drop_time > 360:
                    print("XP NOT FOUND FOR A WHILE STOPPING SCRIPT")
                    self.script_failed = True
                    window_utils.update_status_file(True)
                    break
                self.handle_mining()
                time.sleep(0.5)

        except Exception as e:
            print(f"An error occurred: {e}")
            self.script_failed = True
        finally:
            #logout(self.cursor,self.hwnd)
            window_utils.update_status_file(self.script_failed)

        return self.script_failed

if __name__ == "__main__":
    bot = FishingBot()
    bot.mine()