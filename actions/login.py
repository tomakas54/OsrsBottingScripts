import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.image_recognition_utils import *
from utils.coordinates_utils import *
from utils.window_utils import *
from humancursor import SystemCursor
import pyautogui
import time
import random


def get_account_info(filename='account_data.txt'):
    """Reads the account email and password from the specified file."""
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            email = lines[1].strip()
            password = lines[2].strip()
        return email, password
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return None, None
    except Exception as e:
        print(f"An error occurred while reading {filename}: {e}")
        return None, None
def login(cursor,hwnd):
    screenshot_path = take_screenshot(hwnd)
    
    # Example usage
    source_image_path = screenshot_path  # Use the screenshot as the source image
    template_image_path = 'assets/existing_user.png'  # Path to the template image
    random_coordinates = template_match(source_image_path, template_image_path, threshold=0.8)
    print(random_coordinates)    

    if random_coordinates:
        # Get window position
        window_rect = get_window_rect(hwnd)  # Get window position
        window_left, window_top, _, _ = window_rect        

        # Convert relative coordinates to absolute coordinates
        absolute_coordinates = [(x + window_left, y + window_top) for x, y in random_coordinates]
        print(absolute_coordinates)        

        # Click on the first absolute coordinate
        cursor.click_on(absolute_coordinates[0])

        # Read account info from file
        email, password = get_account_info()
        if email is None or password is None:
            print("Failed to retrieve account info. Exiting...")
            return

        # Enter email and password
        pyautogui.write(email, interval=random.uniform(0.1, 0.2))
        time.sleep(random.uniform(0.1, 0.5))
        PressButton('tab')
        pyautogui.write(password, interval=random.uniform(0.1, 0.2))

        screenshot_path = take_screenshot(hwnd)  
        template_image_path = 'assets/login.png'  # Path to the template image
        random_coordinates = template_match(source_image_path, template_image_path, threshold=0.8)
        
        if random_coordinates:
            absolute_coordinates = [(x + window_left, y + window_top) for x, y in random_coordinates]
            print(absolute_coordinates)        
            # Click on the first absolute coordinate
            cursor.click_on(absolute_coordinates[0])

            time.sleep(random.uniform(10, 20))
            PressButton('esc')
    else:
        print("No matches found.")
        
