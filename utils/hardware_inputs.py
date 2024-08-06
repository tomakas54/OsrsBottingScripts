import ctypes
from ctypes import wintypes
import time
import random
user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_XDOWN = 0x0080
MOUSEEVENTF_XUP = 0x0100
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x01000
MOUSEEVENTF_MOVE_NOCOALESCE = 0x2000
MOUSEEVENTF_VIRTUALDESK = 0x4000
MOUSEEVENTF_ABSOLUTE = 0x8000

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

MAPVK_VK_TO_VSC = 0

wintypes.ULONG_PTR = wintypes.WPARAM

keyCodeMap = {
    'tab'               : "0x09",
    'shift'             : "0x10",
    'esc'               : "0x1B",
    '0'                 : "0x30",
    '1'                 : "0x31",
    '2'                 : "0x32",
    '3'                 : "0x33",
    '4'                 : "0x34",
    '5'                 : "0x35",
    '6'                 : "0x36",
    '7'                 : "0x37",
    '8'                 : "0x38",
    '9'                 : "0x39",
    'a'                 : "0x41",
    'b'                 : "0x42",
    'c'                 : "0x43",
    'd'                 : "0x44",
    'e'                 : "0x45",
    'f'                 : "0x46",
    'g'                 : "0x47",
    'h'                 : "0x48",
    'i'                 : "0x49",
    'j'                 : "0x4A",
    'k'                 : "0x4B",
    'l'                 : "0x4C",
    'm'                 : "0x4D",
    'n'                 : "0x4E",
    'o'                 : "0x4F",
    'p'                 : "0x50",
    'q'                 : "0x51",
    'r'                 : "0x52",
    's'                 : "0x53",
    't'                 : "0x54",
    'u'                 : "0x55",
    'v'                 : "0x56",
    'w'                 : "0x57",
    'x'                 : "0x58",
    'y'                 : "0x59",
    'z'                 : "0x5A",
    'space'             : "0x20",
    'f3'                : "0x72",
    'f12'               : "0x7B",

}


def toKeyCode(c):
    keyCode = keyCodeMap[c]
    return int(keyCode, base=16)


class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk, MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg", wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type", wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def PressMouseButton(button):
    if button == 'left':
        event = MOUSEEVENTF_LEFTDOWN
    elif button == 'right':
        event = MOUSEEVENTF_RIGHTDOWN
    elif button == 'middle':
        event = MOUSEEVENTF_MIDDLEDOWN
    else:
        raise ValueError("Invalid button specified. Use 'left', 'right', or 'middle'.")
    
    x = INPUT(type=INPUT_MOUSE,
              mi=MOUSEINPUT(dwFlags=event))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def ReleaseMouseButton(button):
    if button == 'left':
        event = MOUSEEVENTF_LEFTUP
    elif button == 'right':
        event = MOUSEEVENTF_RIGHTUP
    elif button == 'middle':
        event = MOUSEEVENTF_MIDDLEUP
    else:
        raise ValueError("Invalid button specified. Use 'left', 'right', or 'middle'.")
    
    x = INPUT(type=INPUT_MOUSE,
              mi=MOUSEINPUT(dwFlags=event))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))



def PressButton(button):
    input_key = toKeyCode(button)
    PressKey(input_key)
    time.sleep(random.uniform(0.1, 0.5))
    ReleaseKey(input_key)

def Click(button):
    PressMouseButton(button)
    time.sleep(random.uniform(0.1, 0.2))
    ReleaseMouseButton(button)
    time.sleep(random.uniform(0.1, 0.2))

def WriteString(string):
    for char in string:
        if char.lower() in keyCodeMap:
            PressButton(char.lower())
        elif char == ' ':
            PressButton('space')
        else:
            raise ValueError(f"Unsupported character: {char}")

