from screen import Screen
import cv2
from config import Config
from utils.misc import cut_roi
import mouse
import keyboard
import os
import time
from screen import grab, convert_monitor_to_screen

class GenOcrTruth:
    def __init__(self):
        os.makedirs("log/screenshots/generated", exist_ok=True)
        os.system(f"cd log/screenshots/generated && mkdir ground-truth")
        self._half_width = Config().ui_pos["screen_width"] // 2
        self._half_height = Config().ui_pos["screen_height"] // 2
        self._upper_left = None

    def hook(self, e):
        if e.event_type == "down":
            if e.name == "f12":
                os._exit(1)
            img = grab()
            loc_monitor = mouse.get_position()
            loc_screen = convert_monitor_to_screen(loc_monitor)
            if e.name == "f8":
                # start template
                if self._upper_left is None:
                    self._upper_left = loc_screen
                    print(f"stored upper left: {self._upper_left}")
                    print("Select bottom-right corner of template to create and press f8")
                    return
                # finish template
                else:
                    bottom_right = loc_screen
                    if bottom_right == self._upper_left:
                        print(f"roi failed, try again")
                        self._upper_left = None
                        return
                    print(f"stored bottom_right: {bottom_right}")
                    try:
                        width = (bottom_right[0] - self._upper_left[0])
                        height = (bottom_right[1] - self._upper_left[1])
                        template_img = cut_roi(img, [*self._upper_left, width, height])
                        basename = f"log/screenshots/generated/ground-truth/{time.strftime('%Y%m%d_%H%M%S')}"
                        cv2.imshow(time.strftime('%Y%m%d_%H%M%S'), template_img)
                        cv2.waitKey(1)
                        print(f"new template: {basename} = ")
                        print(f"Enter true text:")
                        truth = input()
                        if truth:
                            with open(f"{basename}.gt.txt", 'w') as f:
                                f.write(truth)
                            cv2.imwrite(f"{basename}.png", template_img)
                            cv2.destroyAllWindows()
                            cv2.waitKey(1)
                            print(f"saved {basename}")
                        else:
                            print(f"skipped {basename}")
                    except:
                        print(f"template save failed, try again")
                    self._upper_left = None
                    print("Select top-left corner of template to create and press f8 | F12 to exit")
                    return
            else:
                return

if __name__ == "__main__":
    keyboard.add_hotkey('f12', lambda: print('Force Exit (f12)') or os._exit(1))
    recorder = GenOcrTruth()
    print("Select top-left corner of template to create and press f8 | F12 to exit")
    keyboard.hook(recorder.hook, suppress=True)
    while True: pass