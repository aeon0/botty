import cv2
import numpy as np
from utils.misc import color_filter
from screen import Screen
from item_finder import ItemFinder
from config import Config
from template_finder import TemplateFinder


def run_graphic_debugger():
    config = Config()
    screen = Screen(config.general["monitor"])
    item_finder = ItemFinder()
    template_finder = TemplateFinder(screen)
    search_templates = ["A5_TOWN_0", "A5_TOWN_1", "A5_TOWN_2", "A5_TOWN_3"]
    while 1:
        img = screen.grab()
        # Show item detections
        combined_img = np.zeros(img.shape, dtype="uint8")
        for key in config.colors:
            _, filterd_img = color_filter(img, config.colors[key])
            combined_img = cv2.bitwise_or(filterd_img, combined_img)
        item_list = item_finder.search(img)
        for item in item_list:
            cv2.circle(combined_img, item.center, 7, (0, 0, 255), 4)
            cv2.putText(combined_img, item.name, item.center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        if len(item_list) > 0:
            print(item_list)
        # Show Town A5 template matches
        scores = {}
        for template_name in search_templates:
            template_match = template_finder.search(template_name, img, threshold=0.65)
            if template_match.valid:
                scores[template_match.name] = template_match.score
                cv2.putText(combined_img, str(template_name), template_match.position, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.circle(combined_img, template_match.position, 7, (255, 0, 0), thickness=5)
        if len(scores) > 0:
            print(scores)
        # Show img
        combined_img = cv2.resize(combined_img, None, fx=0.5, fy=0.5)
        cv2.imshow("debug img", combined_img)
        cv2.setWindowProperty("debug img", cv2.WND_PROP_TOPMOST, 1)
        cv2.waitKey(1)


if __name__ == "__main__":
    run_graphic_debugger()
