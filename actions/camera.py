import time
import random
import sys
import os
from humancursor import SystemCursor
from rich.console import Console
from rich.traceback import install
# Import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from simpy.library import io
from simpy.library.global_vals import *
from utils import window_utils, coordinates_utils, image_recognition_utils,hardware_inputs,constants
console = Console()
install()
class Camera:
    def __init__(self) -> None:
        self.coordinates_utils = coordinates_utils.Coordinates()
        self.image_recognition_utils = image_recognition_utils.ImageRecognition()
        self.cursor = SystemCursor()
        
    def calibrate_camera_rotation(self,rotation = 'north'):
        roi_compass = (*constants.RELATIVE_COORDS["compass"], *constants.ROI_SIZES["compass"])
        compass_coords = self.coordinates_utils.generate_random_coord_in_roi(roi_compass)
        console.log(compass_coords)
        self.coordinates_utils.click_coordinates(compass_coords,'right')
        time.sleep(1)
        if rotation == 'west':
            template_path = 'assets/west.png'
        elif rotation == 'north':
            template_path = 'assets/north.png'
        elif rotation == 'east':
            template_path = 'assets/east.png'
        elif rotation == 'south':
            template_path = 'assets/south.png'
        else:
            console.log('Input rotation as north,west,east,south!')
            return
        rotation_coord = self.image_recognition_utils.generate_random_b_box_coord(self.image_recognition_utils.template_match(template_path))
        console.log(rotation_coord)
        io.wind_mouse(rotation_coord[0][0], rotation_coord[0][1], speed=0.2)
        hardware_inputs.Click('left')
        hardware_inputs.HoldButton('up_arrow', random.uniform(2,4))

    def calibrate_camera_zoom(self,ammount: int, scroll_type) -> None:
        roi = (*constants.RELATIVE_COORDS['bank'],*constants.ROI_SIZES['bank'])
        self.cursor.move_to(self.coordinates_utils.generate_random_coord_in_roi(roi))
        hardware_inputs.ScrollMouse(ammount,scroll_type)
        
            
    def rotate_camera_till_color(self,color):
        # Initial screenshot and color search
        found_color = len(self.coordinates_utils.find_color_coordinates(color)) > 0
        rotate_type = None  # To store the last rotation direction
        rotate_directions = ['right_arrow', 'left_arrow']
        rotate_type = random.choice(rotate_directions)
            
        # Perform the rotation
        hardware_inputs.PressKey(rotate_type) 
        while not found_color:
            # Randomly select a rotation direction
            hardware_inputs.PressKey(rotate_type) 


            found_color = len(self.coordinates_utils.find_color_coordinates(color)) > 0

            # console.log the number of color coordinates found (for debugging)
            console.log(len(self.coordinates_utils.find_color_coordinates(color)))

        # Optionally, stop the camera rotation after finding the color
        if rotate_type is not None:
            hardware_inputs.ReleaseKey(rotate_type) 

        console.log("Color found, rotation stopped.")
        hardware_inputs.ReleaseKey(rotate_type)

if __name__ == "__main__":
    camera = Camera()
    camera.calibrate_camera_rotation('west')
    camera.calibrate_camera_zoom(15,"down")