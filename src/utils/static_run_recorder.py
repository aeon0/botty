from tracemalloc import start
from screen import convert_monitor_to_screen, start_detecting_window, stop_detecting_window
import mouse
import keyboard
from logger import Logger
import os

if __name__ == "__main__":

    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or stop_detecting_window() or os._exit(1))
    Logger.debug("Start with F11")
    start_detecting_window()
    keyboard.wait("f11")

    pos_list = []
    while 1:
        mouse.wait(button=mouse.RIGHT, target_types=mouse.DOWN)
        monitor_pos = mouse.get_position()
        screen_pos = convert_monitor_to_screen(monitor_pos)
        pos_list.append(screen_pos)
        code = ""
        for pos in pos_list:
            code += f"{pos[0]},{pos[1]}, "
        print(code)
