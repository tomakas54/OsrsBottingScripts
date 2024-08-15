import win32gui
import pyautogui
import pygetwindow as gw
import cv2
import numpy as np
from rich.console import Console
from rich.traceback import install
import time
import random

# Set up Rich for better console logging and traceback handling
console = Console()
install()

def get_window_rect(hwnd):
    """Returns the width and height of the window with the specified handle."""
    window = gw.Window(hwnd)
    rect = window._rect
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    return width, height

def get_account_name(filename='account_data.txt'):
    """Reads the account name from the specified file."""
    try:
        with open(filename, 'r') as file:
            name = file.readline().strip()
        return name
    except FileNotFoundError:
        console.log(f"Error: {filename} not found.")
        return None
    except Exception as e:
        console.log(f"An error occurred while reading {filename}: {e}")
        return None
    
def update_status_file(status):
    """Updates the script status file with 'failed' or 'success'."""
    with open('script_status.txt', 'w') as file:
        file.write('failed' if status else 'success')

class ScreenshotManager:
    def __init__(self):
        self.account_name = get_account_name()
        self.hwnd = self.find_runelite_window(self.account_name)
        self.screenshot_path = 'screenshot.png'
        
    def move_window_to_top_right(self, hwnd, width, height):
        """Moves the specified window to the top-left corner of the screen."""
        x, y = 0, 0  # Top-left corner
        win32gui.MoveWindow(hwnd, x, y, width, height, True)
                
    def find_runelite_window(self, account_name) -> int:
        """Finds the RuneLite window based on the account name or fallback to default RuneLite window."""
        hwnd = win32gui.FindWindow(None, f"RuneLite - {account_name}")
        console.log('find_runelite_window: ', hwnd)
        
        if hwnd == 0:
            hwnd = win32gui.FindWindow(None, "RuneLite")
            console.log('find_runelite_window: ', hwnd)

        if hwnd == 0:
            raise Exception(f"Window with name 'RuneLite - {account_name}' or 'RuneLite' not found.")

        # Specify the window size and move to top-left corner
        window_width, window_height = 789, 543
        self.move_window_to_top_right(hwnd, window_width, window_height)
        win32gui.SetActiveWindow(hwnd)
        
        return hwnd
    
    def take_screenshot(self):
        """Takes a screenshot of the specified window and saves it to a file."""
        time.sleep(random.uniform(0.25,0.35))  # Wait for window to stabilize

        if not self.hwnd:
            console.log("Window handle is invalid or not found.")
            return

        try:
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            width, height = right - left, bottom - top
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            screenshot_export = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            cv2.imwrite(self.screenshot_path, screenshot_export)
        except Exception as e:
            console.log(f"Error taking screenshot: {e}")

    def get_screenshot_path(self):
        """Returns the path of the last saved screenshot."""
        return self.screenshot_path

if __name__ == "__main__":
    try:
        sm = ScreenshotManager()
        sm.take_screenshot()
        update_status_file(False)  # Update status to 'success'
    except Exception as e:
        console.log(f"An error occurred: {e}")
        update_status_file(True)  # Update status to 'failed'
