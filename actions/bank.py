import time
import random
import sys
import os
from humancursor import SystemCursor
# Import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import window_utils, coordinates_utils, image_recognition_utils,hardware_inputs
from simpy.library import io
from simpy.library.global_vals import *
COLORS = {
    "bank": [(255, 0, 255)],
}
RELATIVE_COORDS = {
    "bank": (72, 100),
}
ROI_SIZES = {
    "bank": (390, 250),
}

pin_entered = False
def enter_pin(hwnd : int) -> None:
    global pin_entered
    screenshot_path = window_utils.take_screenshot(hwnd)
    pin_matches = image_recognition_utils.template_match(
        screenshot_path,
        'assets/bank_pin_flag.png',
        threshold=0.8
    )
    if len(pin_matches) > 0:
        time.sleep(random.uniform(0.33,0.89))
        f = open("account_data.txt", "r")
        lines = f.readlines()
        hardware_inputs.Write(lines[3].strip())
        time.sleep(random.uniform(1,2))
        pin_entered = True
        return 
    else:
        pin_entered = True
        print('NO PIN NEEDED')
        return

def set_quantity(hwnd : int,quantity : int,cursor) -> None:
    open_bank(hwnd,cursor)
    if is_in_bank(hwnd):
        screenshot_path = window_utils.take_screenshot(hwnd)
        custom_quantity = False
        if quantity == 1:
            print('PICKED 1')
            quantity_coords = image_recognition_utils.generate_random_b_box_coord(
                image_recognition_utils.template_match(
                screenshot_path,
                'assets/quantity_1.png',
                threshold=0.8,
                scaling_factor=0.8
            ))
        elif quantity == 5:
            print('PICKED 5')
            quantity_coords = image_recognition_utils.generate_random_b_box_coord(
                image_recognition_utils.template_match(
                screenshot_path,
                'assets/quantity_5.png',
                threshold=0.8,
                scaling_factor=0.8
            ))
        elif quantity == 10:
            print('PICKED 10')
            quantity_coords = image_recognition_utils.generate_random_b_box_coord(
                image_recognition_utils.template_match(
                screenshot_path,
                'assets/quantity_10.png',
                threshold=0.8,
                scaling_factor=0.8
            ))
        elif quantity >= 28:
            print('PICKED ALL')
            quantity_coords = image_recognition_utils.generate_random_b_box_coord(
                image_recognition_utils.template_match(
                screenshot_path,
                'assets/quantity_all.png',
                threshold=0.8,
                scaling_factor=0.8
            ))
        else:
            print('PICKED X')
            quantity_coords = image_recognition_utils.generate_random_b_box_coord(
                image_recognition_utils.template_match(
                screenshot_path,
                'assets/quantity_x.png',
                threshold=0.8,
                scaling_factor=1
            ))
            custom_quantity = True

        if not custom_quantity:
            coordinates_utils.click_coordinates(cursor,quantity_coords[0])
        else:
            coordinates_utils.click_coordinates(cursor,quantity_coords[0],'right')
            time.sleep(random.uniform(0.4,0.6))
            screenshot_path = window_utils.take_screenshot(hwnd)
            custom_quantity_coords = image_recognition_utils.generate_random_b_box_coord(
                image_recognition_utils.template_match(
                screenshot_path,
                'assets/custom_quantity_text.png',
                threshold=0.8,
                scaling_factor=0.8
            ))
            time.sleep(random.uniform(0.25,0.5))
            io.wind_mouse(custom_quantity_coords[0][0], custom_quantity_coords[0][1], speed=0.2)
            hardware_inputs.Click('left')
            time.sleep(random.uniform(0.25,0.5))
            hardware_inputs.Write(str(quantity))
            hardware_inputs.PressButton('enter')

def is_in_bank(hwnd : int) -> bool:
    screenshot_path = window_utils.take_screenshot(hwnd) 
    bank_item_coords = image_recognition_utils.generate_random_b_box_coord(
        image_recognition_utils.template_match(
            screenshot_path,
            'assets/in_bank_flag.png',
            threshold=0.8,
            scaling_factor=0.5
        ))
    if len(bank_item_coords) > 0:
        print('IN BANK')
        return True
    else:
        return False
    
def open_bank(hwnd : int, cursor : SystemCursor) -> None:
    screenshot, window_left, window_top, window_width, window_height = window_utils.get_window_screenshot(hwnd)
    bank_coords = coordinates_utils.find_color_coordinates(screenshot, COLORS["bank"], roi=(0, 0, window_width, window_height))
    if len(bank_coords) > 0:
        coordinates_utils.click_coordinates(
            cursor,
            coordinates_utils.pick_random_coordinate(
                bank_coords,
                window_left,
                window_top
            ))
        time.sleep(random.uniform(0.6, 0.7))        
    else:
        print('NO BANK FOUND')
        return

def bank_inventory(hwnd : int, cursor : SystemCursor) -> None:
        if not is_in_bank(hwnd):
            global pin_entered
            open_bank(hwnd,cursor)
            if not pin_entered:
                enter_pin(hwnd)
            screenshot_path = window_utils.take_screenshot(hwnd)
            bank_item_coords = image_recognition_utils.generate_random_b_box_coord(
                image_recognition_utils.template_match(
                    screenshot_path,
                    'assets/bank_items.png',
                    threshold=0.8,
                    scaling_factor=0.5
                ))
            coordinates_utils.click_coordinates(cursor,bank_item_coords[0])
            time.sleep(random.uniform(0.6, 0.7))
        else:
            print("CANT FIND BANK")
            return

def take_item(hwnd,cursor,template_path) -> bool:
    if is_in_bank(hwnd):
        no_item = True
        bank_roi = (*RELATIVE_COORDS['bank'],*ROI_SIZES['bank'])
        screenshot_path = window_utils.take_screenshot(hwnd) 
        item_coords = image_recognition_utils.generate_random_b_box_coord(
            image_recognition_utils.template_match(
                screenshot_path,
                template_path,
                threshold=0.8,
                roi=bank_roi,
                scaling_factor=0.8
            ))
        coordinates_utils.click_coordinates(cursor,item_coords[0])
        time.sleep(random.uniform(0.5,0.7))
        screenshot_path = window_utils.take_screenshot(hwnd)
        no_items_matches = image_recognition_utils.template_match(
                screenshot_path,
                'assets/choose.png',
                threshold=0.8,
                roi=bank_roi,
                scaling_factor=0.8
            )
        if len(no_items_matches) > 0:
            print('ZERO ITEM QUANTITY')
            no_item = True
            return no_item
        else:
            return False
    else:
        print('NOT IN BANK')
        return True
     

if __name__ == "__main__":
    cursor = SystemCursor()
    hwnd = window_utils.findWindow_runelite('GIMGrupiokas')
    enter_pin(hwnd)   