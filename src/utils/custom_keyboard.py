# Currently not used
# But this would be an option to work with PostMessage() instead of SendInput()

import win32api
import win32gui

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
MAPVK_VK_TO_VSC = 0

virtual_key_codes = {
    'control-break processing': 0x03,
    'backspace': 0x08,
    'tab': 0x09,
    'clear': 0x0c,
    'enter': 0x0d,
    'shift': 0x10,
    'ctrl': 0x11,
    'alt': 0x12,
    'pause': 0x13,
    'capslock': 0x14,
    'ime hangul mode': 0x15,
    'ime junja mode': 0x17,
    'ime final mode': 0x18,
    'ime kanji mode': 0x19,
    'esc': 0x1b,
    'ime convert': 0x1c,
    'ime nonconvert': 0x1d,
    'ime accept': 0x1e,
    'ime mode change request': 0x1f,
    'spacebar': 0x20,
    'page up': 0x21,
    'page down': 0x22,
    'end': 0x23,
    'home': 0x24,
    'left': 0x25,
    'up': 0x26,
    'right': 0x27,
    'down': 0x28,
    'select': 0x29,
    'print': 0x2a,
    'execute': 0x2b,
    'print screen': 0x2c,
    'insert': 0x2d,
    'delete': 0x2e,
    'help': 0x2f,
    '0': 0x30,
    '1': 0x31,
    '2': 0x32,
    '3': 0x33,
    '4': 0x34,
    '5': 0x35,
    '6': 0x36,
    '7': 0x37,
    '8': 0x38,
    '9': 0x39,
    'a': 0x41,
    'b': 0x42,
    'c': 0x43,
    'd': 0x44,
    'e': 0x45,
    'f': 0x46,
    'g': 0x47,
    'h': 0x48,
    'i': 0x49,
    'j': 0x4a,
    'k': 0x4b,
    'l': 0x4c,
    'm': 0x4d,
    'n': 0x4e,
    'o': 0x4f,
    'p': 0x50,
    'q': 0x51,
    'r': 0x52,
    's': 0x53,
    't': 0x54,
    'u': 0x55,
    'v': 0x56,
    'w': 0x57,
    'x': 0x58,
    'y': 0x59,
    'z': 0x5a,
    'left windows': 0x5b,
    'right windows': 0x5c,
    'applications': 0x5d,
    'sleep': 0x5f,
    '0': 0x60,
    '1': 0x61,
    '2': 0x62,
    '3': 0x63,
    '4': 0x64,
    '5': 0x65,
    '6': 0x66,
    '7': 0x67,
    '8': 0x68,
    '9': 0x69,
    '*': 0x6a,
    '+': 0x6b,
    'separator': 0x6c,
    '-': 0x6d,
    'decimal': 0x6e,
    '/': 0x6f,
    'f1': 0x70,
    'f2': 0x71,
    'f3': 0x72,
    'f4': 0x73,
    'f5': 0x74,
    'f6': 0x75,
    'f7': 0x76,
    'f8': 0x77,
    'f9': 0x78,
    'f10': 0x79,
    'f11': 0x7a,
    'f12': 0x7b,
    'f13': 0x7c,
    'f14': 0x7d,
    'f15': 0x7e,
    'f16': 0x7f,
    'f17': 0x80,
    'f18': 0x81,
    'f19': 0x82,
    'f20': 0x83,
    'f21': 0x84,
    'f22': 0x85,
    'f23': 0x86,
    'f24': 0x87,
    'num lock': 0x90,
    'scroll lock': 0x91,
    'left shift': 0xa0,
    'right shift': 0xa1,
    'left ctrl': 0xa2,
    'right ctrl': 0xa3,
    'left menu': 0xa4,
    'right menu': 0xa5,
    'browser back': 0xa6,
    'browser forward': 0xa7,
    'browser refresh': 0xa8,
    'browser stop': 0xa9,
    'browser search key': 0xaa,
    'browser favorites': 0xab,
    'browser start and home': 0xac,
    'volume mute': 0xad,
    'volume down': 0xae,
    'volume up': 0xaf,
    'next track': 0xb0,
    'previous track': 0xb1,
    'stop media': 0xb2,
    'play/pause media': 0xb3,
    'start mail': 0xb4,
    'select media': 0xb5,
    'start application 1': 0xb6,
    'start application 2': 0xb7,
    '+': 0xbb,
    ',': 0xbc,
    '-': 0xbd,
    '.': 0xbe,
    'ime process': 0xe5,
    'attn': 0xf6,
    'crsel': 0xf7,
    'exsel': 0xf8,
    'erase eof': 0xf9,
    'play': 0xfa,
    'zoom': 0xfb,
    'reserved ': 0xfc,
    'pa1': 0xfd,
    'clear': 0xfe
}

def _send_event(code, event_type):
    lp = 1
    lp |= 0 << 24
    lp |= (win32api.MapVirtualKey(code, MAPVK_VK_TO_VSC) << 16)

    if (event_type == 2):
        lp |= 0xC0000000
        type = WM_KEYUP
    else:
        type = WM_KEYDOWN

    hwnd = win32gui.FindWindowEx(None, None, None, "Diablo II: Resurrected")
    win32api.PostMessage(hwnd, type, code, lp)

def press(code):
    _send_event(code, 0)

def release(code):
    _send_event(code, 2)

def parse_hotkey(key_str):
    keys = [virtual_key_codes[x.strip()] for x in key_str.split("+")]
    return keys

def send(hotkey, do_press=True, do_release=True):
    """
    Sends OS events that perform the given *hotkey* hotkey.

    - `hotkey` can be either a scan code (e.g. 57 for space), single key
    (e.g. 'space') or multi-key, multi-step hotkey (e.g. 'alt+F4, enter').
    - `do_press` if true then press events are sent. Defaults to True.
    - `do_release` if true then release events are sent. Defaults to True.

        send(57)
        send('ctrl+alt+del')
        send('alt+F4, enter')
        send('shift+s')

    Note: keys are released in the opposite order they were pressed.
    """
    # check keys here
    # http://www.kbdedit.com/manual/low_level_vk_list.html
    parsed = parse_hotkey(hotkey)
    if do_press:
        for virtual_code in parsed:
            press(virtual_code)

    if do_release:
        for virtual_code in reversed(parsed):
            release(virtual_code)
