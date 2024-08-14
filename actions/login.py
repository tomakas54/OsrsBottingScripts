import sys
import os
import pyautogui
import time
import random
from rich.console import Console
from rich.traceback import install
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.image_recognition_utils import *
from utils.coordinates_utils import *
from utils.window_utils import *
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
    
def login(cursor, hwnd: int) -> None:
    _,_,_,_,_,screenshot_path = get_window_screenshot(hwnd)
    console.log(f"Screenshot saved to: {screenshot_path}")
    
    source_image_path = screenshot_path  # Use the screenshot as the source image
    template_image_path = 'assets/existing_user.png'  # Path to the template image
    console.log(f"Source image path: {source_image_path}")
    console.log(f"Template image path: {template_image_path}")

    random_coordinates = generate_random_b_box_coord(template_match(source_image_path, template_image_path, threshold=0.8))
    console.log(f"Random coordinates: {random_coordinates}")

    if random_coordinates:
        # Get window position
        window_rect = get_window_rect(hwnd)  # Get window position
        window_left, window_top, _, _ = window_rect        

        # Convert relative coordinates to absolute coordinates
        absolute_coordinates = [(x + window_left, y + window_top) for x, y in random_coordinates]
        console.log(f"Absolute coordinates: {absolute_coordinates}")

        # Click on the first absolute coordinate
        cursor.click_on(absolute_coordinates[0])

        # Read account info from file
        email, password = get_account_info()
        if email is None or password is None:
            console.log("Failed to retrieve account info. Exiting...")
            return

        # Enter email and password
        pyautogui.write(email, interval=random.uniform(0.1, 0.2))
        time.sleep(random.uniform(0.1, 0.5))
        PressButton('tab')
        pyautogui.write(password, interval=random.uniform(0.1, 0.2))

        _,_,_,_,_,screenshot_path = get_window_screenshot(hwnd) 
        template_image_path = 'assets/login.png'  # Path to the template image
        random_coordinates = generate_random_b_box_coord(template_match(source_image_path, template_image_path, threshold=0.8))
        
        if random_coordinates:
            absolute_coordinates = [(x + window_left, y + window_top) for x, y in random_coordinates]
            console.log(f"Absolute coordinates: {absolute_coordinates}")

            # Click on the first absolute coordinate
            cursor.click_on(absolute_coordinates[0])

            time.sleep(random.uniform(10, 20))
            PressButton('esc')
    else:
        console.log("No matches found.")
        

