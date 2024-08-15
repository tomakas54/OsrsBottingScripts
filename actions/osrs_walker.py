import time
import random
import sys
import os
from humancursor import SystemCursor
import json
import math
import pyautogui
# Import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import window_utils,hardware_inputs,http_getter,walker_utils,constants
from simpy.library import io
from simpy.library.global_vals import *
from typing import List, Tuple





def change_position(new_pos: list):
    '''Clicks the minimap to change position, ensuring click coordinates are within window bounds.'''
    # Define window bounds (example values, adjust as needed)
    WINDOW_WIDTH = 789  # Replace with actual window width
    WINDOW_HEIGHT = 543 # Replace with actual window height

    # Get minimap center
    center_mini = constants.RELATIVE_COORDS["map_center"]

    # Fetch current game data
    data = http_getter.get_game_data('events')
    print(data)
    live_pos_x = data["worldPoint"]["x"]
    live_pos_y = data["worldPoint"]["y"]

    # Compute tiles to click
    tiles = walker_utils.compute_tiles(live_pos_x, live_pos_y, new_pos[0], new_pos[1])
    click_x = center_mini[0] + tiles[0]
    click_y = center_mini[1] + tiles[1]

    # Debug print statements
    print(f"Computed click coordinates: x={click_x}, y={click_y}")

    # Ensure click coordinates are within the window bounds
    click_x = max(0, min(click_x, WINDOW_WIDTH - 20))
    click_y = max(0, min(click_y, WINDOW_HEIGHT - 20))

    print(f"Adjusted click coordinates: x={click_x}, y={click_y}")

    # Perform click

    #coordinates_utils.click_coordinates(cursor, [click_x, click_y])
    io.wind_mouse(click_x, click_y, speed=0.2)
    hardware_inputs.Click('left')
    time.sleep(1)

def is_in_area(starting_area : list) -> bool:
    data = http_getter.get_game_data('events')['worldPoint']
    current_coords = data['x'],data['y']
    starting_area
    if current_coords in starting_area:
        print('IN AREA')
        return True
    else:
        print('NOT IN AREA')
        return False


def walk_to_coordinates_from_starting_area(coords_list: list, start_location_coords : tuple):
    walker_utils.generate_area(start_location_coords[0],start_location_coords[1])
    if is_in_area(start_location_coords):
        for coord in coords_list:
            if len(coord) != 2:
                print(f"Invalid coordinate format: {coord}")
                continue
            
            print(f"Moving to coordinate: {coord}")
            change_position(coord)
            
            # Optional: Add delay to ensure the game processes the movement
            while(current_coords !=coord):
                data = http_getter.get_game_data('events')['worldPoint']
                current_coords = data['x'],data['y']
                walk_count += 1
                if walk_count >50:
                    continue
                time.sleep(0.5)
                
            else:
                continue
    else:
        print('NOT IN A STARTING AREA')
        return
    
def walk_to_coordinates(coords_list: list):
    '''Walks to a list of coordinates sequentially with an optional delay.'''
    data = http_getter.get_game_data('events')['worldPoint']
    current_coords = data['x'],data['y']
    for coord in coords_list:
        if len(coord) != 2:
            print(f"Invalid coordinate format: {coord}")
            continue
        top_left = coord[0]-1,coord[1]+1
        bottom_right = coord[0]+1,coord[1]-1
        area = walker_utils.generate_area(top_left,bottom_right)
        print(f"Moving to coordinate: {coord}")
        change_position(random.choice(area))
        # Optional: Add delay to ensure the game processes the movement
        while current_coords not in area:
            data = http_getter.get_game_data('events')['worldPoint']
            current_coords = data['x'],data['y']
            print('WALKING')
            
            time.sleep(1)
        else:
            continue

if __name__ == "__main__":
    ##while True:
        #data = http_getter.get_game_data('events')['worldPoint']
        #print(data)
        #time.sleep(0.5)    
    #max 18 tiles
    #change_position([3069,3389])
    hwnd = window_utils.findWindow_runelite('GIMGrupiokas')

    walk_to_coordinates([(2946, 3369), (2946, 3372), (2947, 3375), (2949, 3376), (2952, 3378), (2955, 3380), (2960, 3381), (2967, 3381), (2975, 3380), (2979, 3379), (2988, 3376), (2996, 3370), (3000, 3368), (3013, 3362), (3016, 3360), (3019, 3359), (3019, 3355)])
    

