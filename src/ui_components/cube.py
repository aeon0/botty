#	- cube transmute
from config import Config
from template_finder import TemplateMatch
from transmute.inventory_collection import inspect_area
from utils.custom_mouse import mouse
from utils.misc import wait
import keyboard
from ui.ui_manager import UiManager, detect_screen_object, hover_over_screen_object_match, SCREEN_OBJECTS

inventory = inspect_area(total_rows=4, total_columns=3, roi=Config().ui_roi["cube_area_roi"], known_items=[])

def open() -> TemplateMatch:
    match = detect_screen_object(SCREEN_OBJECTS['CubeInventory'])
    if match.valid:
        hover_over_screen_object_match(match)
        mouse.click("right")
        wait(0.1)
        return detect_screen_object(SCREEN_OBJECTS['CubeOpened'])
    return None

def transmute():
    match = detect_screen_object(SCREEN_OBJECTS['CubeOpened'])
    if match.valid:
        mouse.click("left")

def close():
    keyboard.press("esc")

def is_empty() -> bool:
    global inventory
    return inventory.count_empty() == 12

if __name__ == "__main__":
    m = detect_screen_object(SCREEN_OBJECTS['CubeInventory'])
    if m.valid:
        m = open()
        print(f'Empty: {is_empty()}')
        if m.valid:
            transmute()
            close()
