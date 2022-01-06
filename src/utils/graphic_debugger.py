import threading

import cv2
import numpy as np
from utils.misc import color_filter, kill_thread
from screen import Screen
from item import ItemFinder
from config import Config
from template_finder import TemplateFinder


class GraphicDebuggerController:
    """
    This class takes care of handling the graphic debugger by starting and stopping it.

    The variable is_running is static and should be accessed only by the main thread or it is subject
    to race condition, if you plan to touch it from within a thread you might have to
    add a locking mechanism to order to access it.
    """
    is_running = False

    def __init__(self, config: Config):
        self.config = config
        self.screen = None
        self.item_finder = None
        self.template_finder = None
        self.debugger_thread = None

    def start(self):
        self.item_finder = ItemFinder(self.config)
        self.screen = Screen(self.config.general["monitor"])
        self.template_finder = TemplateFinder(self.screen)
        self.debugger_thread = threading.Thread(target=self.run_debugger)
        self.debugger_thread.daemon = False
        self.debugger_thread.start()
        GraphicDebuggerController.is_running = True

    def stop(self):
        if self.debugger_thread: kill_thread(self.debugger_thread)
        GraphicDebuggerController.is_running = False

    def run_debugger(self):
        search_templates = ["INV_TOP_LEFT", "INV_TOP_RIGHT", "INV_BOTTOM_LEFT", "INV_BOTTOM_RIGHT"]
        while 1:
            img = self.screen.grab()
            # Show item detections
            combined_img = np.zeros(img.shape, dtype="uint8")
            for key in self.config.colors:
                _, filterd_img = color_filter(img, self.config.colors[key])
                combined_img = cv2.bitwise_or(filterd_img, combined_img)
            item_list = self.item_finder.search(img)
            for item in item_list:
                cv2.circle(combined_img, item.center, 7, (0, 0, 255), 4)
                cv2.putText(combined_img, item.name, item.center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            if len(item_list) > 0:
                print(item_list)
            # Show Town A5 template matches
            scores = {}
            for template_name in search_templates:
                template_match = self.template_finder.search(template_name, img, threshold=0.65)
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
    debugger = GraphicDebuggerController(Config())
    debugger.start()
