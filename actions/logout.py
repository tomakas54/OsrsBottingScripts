import random
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import constants, hardware_inputs, coordinates_utils

def logout() -> None:
    coord_utils = coordinates_utils.Coordinates()
    roi_inventory = (*constants.RELATIVE_COORDS["inventory"], *constants.ROI_SIZES["inventory"])
    time.sleep(random.uniform(3,5))
    hardware_inputs.PressButton('esc')
    time.sleep(random.uniform(3,5))
    hardware_inputs.PressButton('f12')
    time.sleep(random.uniform(1, 1.5))
    logout_coords = coord_utils.find_color_coordinates(constants.COLORS["logout_button"], roi=roi_inventory)
    print(logout_coords)
    coord_utils.click_coordinates(coord_utils.pick_random_coordinate(logout_coords))

    

