import time
import random
import sys
import os
from humancursor import SystemCursor

# Import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from simpy.library import io
from simpy.library.global_vals import *
from utils import window_utils, coordinates_utils, image_recognition_utils,hardware_inputs,constants


def calibrate_camera(rotation = 'north'):
    cursor = SystemCursor()
    name = window_utils.get_account_name()
    hwnd = window_utils.findWindow_runelite(name)
    roi_compass = (*constants.RELATIVE_COORDS["compass"], *constants.ROI_SIZES["compass"])
    compass_coords = coordinates_utils.generate_random_coord_in_roi(roi_compass)
    print(compass_coords)
    coordinates_utils.click_coordinates(cursor,compass_coords,'right')
    time.sleep(1)
    _,_,_,_,_,screenshot_path = window_utils.get_window_screenshot(hwnd)
    if rotation == 'west':
        template_path = 'assets/west.png'
    elif rotation == 'north':
        template_path = 'assets/north.png'
    elif rotation == 'east':
        template_path = 'assets/east.png'
    elif rotation == 'south':
        template_path = 'assets/south.png'
    else:
        print('Input rotation as north,west,east,south!')
        return
    rotation_coord = image_recognition_utils.generate_random_b_box_coord(image_recognition_utils.template_match(screenshot_path,template_path))
    print(rotation_coord)
    io.wind_mouse(rotation_coord[0][0], rotation_coord[0][1], speed=0.2)
    hardware_inputs.Click('left')
    hardware_inputs.HoldButton('up_arrow', random.uniform(2,4))


if __name__ == "__main__":
    calibrate_camera('east')