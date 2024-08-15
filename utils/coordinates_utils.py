import numpy as np
import random
import time
from rich.console import Console
from rich.traceback import install
from PIL import Image,UnidentifiedImageError
from rich.traceback import install
from utils import constants , window_utils, hardware_inputs
from humancursor import SystemCursor

install()
console = Console()

class Coordinates:
    def __init__(self) -> None:
        self.cursor = SystemCursor()
        self.screenshot_path = window_utils.ScreenshotManager().get_screenshot_path()
        self.screenshot_manager = window_utils.ScreenshotManager()
    
    def load_image_to_array(self):
        self.screenshot_manager.take_screenshot()
        with Image.open(self.screenshot_path) as img:
            img = img.convert('RGB')
            return np.array(img)
    
    def find_color_coordinates(self, target_colors, tolerance=20, roi=None):
        """
        Find coordinates of specified colors in the image.

        Parameters:
        - target_colors: List of target colors to find (each color should be a tuple (R, G, B)).
        - tolerance: Color tolerance for matching.
        - roi: Region of interest as a tuple (x, y, width, height). If None, the whole image is used.

        Returns:
        - An array of coordinates matching the target colors.
        """
        
        # Load image and convert to array
        img_array = self.load_image_to_array()
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


    def pick_random_coordinate(self,coordinates : list) -> tuple:
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
        return (int(relative_coordinate[1]), int(relative_coordinate[0]))


    def click_coordinates(self,coordinates : list, button : str = 'left') -> None:
        """
        Click on the specified coordinates using the cursor.

        Parameters:
        - cursor: The cursor object.
        - coordinates: The coordinates to click.
        """
        if coordinates and button == 'left':
            self.cursor.move_to(coordinates)
            hardware_inputs.Click(button)
        if coordinates and button == 'right':
            self.cursor.move_to(coordinates)
            hardware_inputs.Click(button)
        
            
    def generate_random_absolute_coords(self,abs_x : int, abs_y : int) -> tuple:
        """
        Generate random absolute coordinates within the given range.

        Parameters:
        - abs_x: The maximum x coordinate.
        - abs_y: The maximum y coordinate.

        Returns:
        - A tuple of random absolute x and y coordinates.
        """
        return random.uniform(0, abs_x), random.uniform(0, abs_y)



    def xp_check(self) -> bool:
        roi_xp_drop = (*constants.RELATIVE_COORDS["xp_drop"], *constants.ROI_SIZES["xp_drop"])
        xp_coords = self.find_color_coordinates(constants.COLORS["red"], roi=roi_xp_drop)
        if len(xp_coords) > 0:
            is_xp = True
        else:
            is_xp = False
        return is_xp

    def action_check(self) -> bool:
        roi_action = (*constants.RELATIVE_COORDS["action"], *constants.ROI_SIZES["action"])
        xp_coords = self.find_color_coordinates(constants.COLORS["green"], roi=roi_action)
        if len(xp_coords) > 0:
            is_action = True
        else:
            is_action = False
        return is_action

        
    def generate_random_coord_in_roi(self,roi):
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


if __name__ == "__main__":
    coords = Coordinates()
    while True:
        coordinates = coords.xp_check()
        console.log(coordinates)
        time.sleep(1)