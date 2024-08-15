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
from utils import window_utils, coordinates_utils, image_recognition_utils,hardware_inputs,http_getter
from simpy.library import io
from simpy.library.global_vals import *
from typing import List, Tuple



DEGREES_PER_YAW: float = 360 / 2048

def generate_area(top_left_coord: tuple, bottom_right_coord: tuple, step: int = 1) -> list:
    '''Generates a list of coordinates within a rectangular area defined by starting and ending coordinates.'''
    x_start, y_start = top_left_coord
    x_end, y_end = bottom_right_coord

    # Ensure correct order
    x_start, x_end = min(x_start, x_end), max(x_start, x_end)
    y_start, y_end = min(y_start, y_end), max(y_start, y_end)

    # Print debug information
    print(f"Top-left corner: ({x_start}, {y_start})")
    print(f"Bottom-right corner: ({x_end}, {y_end})")
    print(f"Step size: {step}")
    
    locations = []
    # Generate coordinates within the specified rectangle
    for x in range(x_start, x_end + 1, step):
        for y in range(y_start, y_end + 1, step):
            locations.append((x, y))

    # Print debug information for generated locations
    print(f"Generated {len(locations)} coordinates.")
    print(f"Sample coordinates: {locations[:10]}")  # Print a sample of the coordinates

    return locations  # Ensure the function returns the list of coordinates

def generate_path_coordinates(destination: tuple, step: int = 1) -> list:
    '''
    Generates a list of coordinates from a starting point to a destination point.

    :param start: Starting coordinate as (x, y).
    :param destination: Destination coordinate as (x, y).
    :param step: Step size for generating intermediate coordinates.
    :return: List of coordinates from start to destination.
    '''
    data = http_getter.get_game_data('events')['worldPoint']
    dest_x, dest_y = destination

    # Calculate the distance and direction
    delta_x = dest_x - data['x']
    delta_y = dest_y - data['y']
    distance = math.sqrt(delta_x**2 + delta_y**2)

    if distance == 0:
        return data

    # Number of steps required
    num_steps = int(distance / step)
    if num_steps == 0:
        num_steps = 1  # At least one step

    # Generate coordinates
    path_coords = []
    for i in range(num_steps + 1):
        # Calculate the intermediate point
        ratio = i / num_steps
        x = data['x'] + ratio * delta_x
        y = data['y'] + ratio * delta_y
        path_coords.append((round(x), round(y)))

    return path_coords


def generate_multiple_areas(areas: dict, step: int = 1) -> list:
    '''
    Generates a list of coordinates within multiple rectangular areas defined by the dictionary.
    
    :param areas: Dictionary where keys are area names and values are tuples of (top_left_coord, bottom_right_coord).
    :param step: Step size for generating coordinates.
    :return: List of coordinates within all specified areas.
    '''
    all_locations = {}

    for area_name, coords in areas.items():
        top_left_coord, bottom_right_coord = coords
        x_start, y_start = top_left_coord
        x_end, y_end = bottom_right_coord
        location = []
        # Ensure correct order
        x_start, x_end = min(x_start, x_end), max(x_start, x_end)
        y_start, y_end = min(y_start, y_end), max(y_start, y_end)

        # Print debug information
        print(f"Area '{area_name}' - Top-left corner: ({x_start}, {y_start})")
        print(f"Area '{area_name}' - Bottom-right corner: ({x_end}, {y_end})")
        print(f"Area '{area_name}' - Step size: {step}")

        # Generate coordinates within the specified rectangle
        for x in range(x_start, x_end + 1, step):
            for y in range(y_start, y_end + 1, step):
                location.append((x, y))

        all_locations[area_name] = location

    return all_locations



def compute_tiles(live_x: int, live_y: int, new_x: int, new_y: int) -> list:
    '''Returns the range to click from the minimap center in amount of tiles.'''
    # Get live camera data.
    camera_data = http_getter.get_game_data('events')['camera']
    print("camera data:", camera_data)
    while camera_data is None:
        camera_data = http_getter.get_game_data('events')['camera']
    if camera_data != None:
        # Get camera angle.
        yaw = camera_data['yaw']
        # Account for anticlockwise OSRS minimap.
        degrees = 360 - DEGREES_PER_YAW * yaw
        # Turn degrees into pi-radians.
        theta = math.radians(degrees)
        # Turn position difference into pixels difference.
        x_reg = (new_x - live_x) * 4
        y_reg = (live_y - new_y) * 4
        # Formulas to compute norm of a vector in a rotated coordinate system.
        tiles_x = x_reg * math.cos(theta) + y_reg * math.sin(theta)
        tiles_y = -x_reg * math.sin(theta) + y_reg * math.cos(theta)
        return [round(tiles_x, 1), round(tiles_y, 1)]
    return [live_x, live_y]
