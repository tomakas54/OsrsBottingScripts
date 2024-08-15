import sys
import os
import pyautogui
import time
import random
from rich.console import Console
from rich.traceback import install
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import image_recognition_utils, hardware_inputs, coordinates_utils
console = Console()
install()

def get_account_info(filename='account_data.txt') -> tuple:
    """
    Reads the account email and password from the specified file.

    Parameters:
    - filename: The name of the file containing the account information.

    Returns:
    - A tuple containing the email and password, or (None, None) if an error occurs.
    """
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            email = lines[1].strip()
            password = lines[2].strip()
        return email, password
    except FileNotFoundError:
        console.log(f"Error: {filename} not found.")
        return None, None
    except Exception as e:
        console.log(f"An error occurred while reading {filename}: {e}")
        return None, None
    
def login() -> None:
    img_utils = image_recognition_utils.ImageRecognition()
    coord_utils = coordinates_utils.Coordinates()
    template_image_path = 'assets/existing_user.png'  # Path to the template image
    random_coordinates = img_utils.generate_random_b_box_coord(
        img_utils.template_match(
            template_image_path, 
            threshold=0.8
            ))

    if len(random_coordinates) > 0:
        console.log(random_coordinates)
        coord_utils.click_coordinates(random_coordinates[0])
        # Read account info from file
        email, password = get_account_info()
        if email is None or password is None:
            console.log("Failed to retrieve account info. Exiting...")
            return
        # Enter email and password
        pyautogui.write(email, interval=random.uniform(0.1, 0.2))
        time.sleep(random.uniform(0.1, 0.5))
        hardware_inputs.PressButton('tab')
        pyautogui.write(password, interval=random.uniform(0.1, 0.2))

        template_image_path = 'assets/login.png'  # Path to the template image
        random_coordinates = img_utils.generate_random_b_box_coord(
            img_utils.template_match(
                template_image_path, 
                threshold=0.8
                ))
        
        if len(random_coordinates) > 0:
            # Click on the first absolute coordinate
            coord_utils.click_coordinates(random_coordinates[0])
            time.sleep(random.uniform(10, 20))
            hardware_inputs.PressButton('esc')
    else:
        console.log("No matches found.")

        

