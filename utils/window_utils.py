import win32api
import win32gui
import pyautogui
import pygetwindow as gw

def move_window_to_top_right(hwnd, window_width, window_height):
    # Get the screen resolution
    screen_width = win32api.GetSystemMetrics(0)  # Get screen width

    # Calculate the top-right corner position
    x = 0
    y = 0  # Top of the screen

    # Move the window
    win32gui.MoveWindow(hwnd, x-10, y, window_width, window_height, True)

def findWindow_runelite(Name):
    global hwnd
    hwnd = win32gui.FindWindow(None, "RuneLite - " + Name)
    print('findWindow_runelite: ', hwnd)

    # Specify the window size
    window_width = 789
    window_height = 543

    move_window_to_top_right(hwnd, window_width, window_height)
    win32gui.SetActiveWindow(hwnd)
    
    return hwnd
    
def get_window_screenshot(hwnd):
    """Capture a screenshot of the specified window."""
    if hwnd == 0:
        raise Exception("Window handle is invalid")
    
    # Get the window's position and size
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top
    
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    return screenshot, left, top, width, height


def get_window_rect(hwnd):
    window = gw.Window(hwnd)
    rect = window._rect
    return (rect.left, rect.top, rect.right, rect.bottom)


def get_account_name(filename='account_data.txt'):
    """Reads the account name from the specified file."""
    try:
        with open(filename, 'r') as file:
            name = file.readline().strip()
        return name
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading {filename}: {e}")
        return None
    
def update_status_file(status):
    with open('script_status.txt', 'w') as file:
        file.write('failed' if status else 'success')