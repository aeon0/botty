from screen import Screen
from config import Config
import mouse


if __name__ == "__main__":
    pos_list = []
    config = Config()
    screen = Screen()
    while 1:
        mouse.wait(button=mouse.RIGHT, target_types=mouse.DOWN)
        monitor_pos = mouse.get_position()
        screen_pos = screen.convert_monitor_to_screen(monitor_pos)
        pos_list.append(screen_pos)
        code = ""
        for pos in pos_list:
            code += f"{pos[0]},{pos[1]}, "
        print(code)
