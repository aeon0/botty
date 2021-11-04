import mouse
import keyboard

if __name__ == "__main__":
    pos_list = []
    while 1:
        keyboard.wait("f11")
        pos_list.append(mouse.get_position())
        print(pos_list)
