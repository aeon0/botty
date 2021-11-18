import cv2
import numpy as np
from utils.misc import color_filter
from screen import Screen
from item_finder import ItemFinder
from config import Config


def run_color_checker():
    config = Config()
    screen = Screen(config.general["monitor"])
    item_finder = ItemFinder()
    while 1:
        img = screen.grab()
        combined_img = np.zeros(img.shape, dtype="uint8")
        for key in config.colors:
            _, filterd_img = color_filter(img, config.colors[key])
            combined_img = cv2.bitwise_or(filterd_img, combined_img)
        item_list = item_finder.search(img)
        for item in item_list:
            cv2.circle(combined_img, item.center, 7, (0, 0, 255), 4)
        combined_img = cv2.resize(combined_img, None, fx=0.5, fy=0.5)
        cv2.imshow("debug img", combined_img)
        cv2.setWindowProperty("debug img", cv2.WND_PROP_TOPMOST, 1)
        cv2.waitKey(1)


if __name__ == "__main__":
    run_color_checker()
