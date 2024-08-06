import numpy as np
import random
from utils.hardware_inputs import *
def find_color_coordinates(image, target_colors, tolerance=20, roi=None):
    """Find coordinates of specified colors in the image."""
    img_array = np.array(image)
    if roi:
        x_start, y_start, width, height = roi
        img_array = img_array[y_start:y_start+height, x_start:x_start+width]
    
    all_coordinates = []
    for target_color in target_colors:
        diff = np.abs(img_array - target_color)
        match = np.all(diff <= tolerance, axis=-1)
        coordinates = np.argwhere(match)
        if roi:
            coordinates += [y_start, x_start]
        all_coordinates.extend(coordinates)
    
    return np.array(all_coordinates)

def get_absolute_coordinates(window_left, window_top, relative_x, relative_y):
    """Convert relative coordinates to absolute screen coordinates."""
    absolute_x = window_left + relative_x
    absolute_y = window_top + relative_y
    return absolute_x, absolute_y

def pick_random_coordinate(coordinates, window_left, window_top):
    """Select a random coordinate from the list and convert to absolute."""
    if coordinates.size == 0:
        return None
    relative_coordinate = random.choice(coordinates)
    absolute_coordinate = get_absolute_coordinates(window_left, window_top, int(relative_coordinate[1]), int(relative_coordinate[0]))
    return absolute_coordinate

def click_coordinates(cursor, coordinates):
    """Click on the specified coordinates using the cursor."""
    if coordinates:
        cursor.move_to(coordinates)
        Click('left')
        
def generate_random_absolute_coords(abs_x,abs_y):
    x = random.uniform(0,abs_x)
    y = random.uniform(0,abs_y)
    rand_abs_coords = x,y
    return rand_abs_coords

