import numpy as np
import random
from utils.hardware_inputs import *

def find_color_coordinates(image, target_colors, tolerance=20, roi=None):
    """
    Find coordinates of specified colors in the image.

    Parameters:
    - image: The input image.
    - target_colors: List of target colors to find.
    - tolerance: Color tolerance for matching.
    - roi: Region of interest as a tuple (x, y, width, height). If None, the whole image is used.

    Returns:
    - An array of coordinates matching the target colors.
    """
    img_array = np.array(image)
    if roi:
        x_start, y_start, width, height = roi
        img_array = img_array[y_start:y_start + height, x_start:x_start + width]

    all_coordinates = []
    for target_color in target_colors:
        diff = np.abs(img_array - target_color)
        match = np.all(diff <= tolerance, axis=-1)
        coordinates = np.argwhere(match)
        if roi:
            coordinates += [y_start, x_start]
        all_coordinates.extend(coordinates)

    return np.array(all_coordinates)

def get_absolute_coordinates(window_left : int, window_top : int, relative_x : int, relative_y : int) -> tuple:
    """
    Convert relative coordinates to absolute screen coordinates.

    Parameters:
    - window_left: The left position of the window.
    - window_top: The top position of the window.
    - relative_x: Relative x coordinate.
    - relative_y: Relative y coordinate.

    Returns:
    - A tuple of absolute x and y coordinates.
    """
    return window_left + relative_x, window_top + relative_y

def pick_random_coordinate(coordinates : list, window_left : int, window_top : int) -> tuple:
    """
    Select a random coordinate from the list and convert to absolute.

    Parameters:
    - coordinates: List of relative coordinates.
    - window_left: The left position of the window.
    - window_top: The top position of the window.

    Returns:
    - A tuple of absolute coordinates, or None if the list is empty.
    """
    if len(coordinates) == 0:
        return None
    relative_coordinate = random.choice(coordinates)
    return get_absolute_coordinates(window_left, window_top, int(relative_coordinate[1]), int(relative_coordinate[0]))


def click_coordinates(cursor, coordinates : list, button : str = 'left') -> None:
    """
    Click on the specified coordinates using the cursor.

    Parameters:
    - cursor: The cursor object.
    - coordinates: The coordinates to click.
    """
    if coordinates and button == 'left':
        cursor.move_to(coordinates)
        Click(button)
    if coordinates and button == 'right':
        cursor.move_to(coordinates)
        Click(button)
    
        
def generate_random_absolute_coords(abs_x : int, abs_y : int) -> tuple:
    """
    Generate random absolute coordinates within the given range.

    Parameters:
    - abs_x: The maximum x coordinate.
    - abs_y: The maximum y coordinate.

    Returns:
    - A tuple of random absolute x and y coordinates.
    """
    return random.uniform(0, abs_x), random.uniform(0, abs_y)



def xp_check(screenshot) -> bool:
    RELATIVE_COORDS = {
        "xp_drop": (450, 76),
    }
    ROI_SIZES = {
        "xp_drop": (60, 100),
    }
    COLORS = {
        "xp_drop": [(255, 0, 0)]
    }
    roi_xp_drop = (*RELATIVE_COORDS["xp_drop"], *ROI_SIZES["xp_drop"])
    xp_coords = find_color_coordinates(screenshot, COLORS["xp_drop"], roi=roi_xp_drop)
    if len(xp_coords) > 0:
        is_xp = True
    else:
        is_xp = False
    return is_xp

def generate_random_coord_in_roi(roi):
    """
    Generate a random coordinate within the specified ROI.

    Parameters:
    - roi: Region of interest as a tuple (x, y, width, height).

    Returns:
    - A tuple of random coordinates (x, y) within the ROI.
    """
    x_start, y_start, width, height = roi
    random_x = random.uniform(x_start, x_start + width)
    random_y = random.uniform(y_start, y_start + height)
    return int(random_x), int(random_y)



