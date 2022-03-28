from screen import convert_monitor_to_screen
import mouse

if __name__ == "__main__":
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
