import threading
import time

import cv2
import numpy as np
from utils.misc import color_filter, kill_thread
from screen import Screen
from item import ItemFinder
from config import Config
from template_finder import TemplateFinder
import tkinter as tk
from PIL import ImageTk, Image


class GraphicDebuggerController:
    """
    This class takes care of handling the window_name by starting and stopping it.

    The variable is_running is static and should be accessed only by the main thread or it is subject
    to race condition, if you plan to touch it from within a thread you might have to
    add a locking mechanism to order to access it.
    """
    is_running = False
    window_name_trackbars = "Graphic Debugger - Trackbars"
    window_name_images = "Graphic Debugger - Images"

    def __init__(self, config: Config):
        self._config = config
        self.screen = None
        self.item_finder = None
        self.template_finder = None
        self.debugger_thread = None
        self.ui_thread = None
        self.ui_lock = threading.Lock()
        self.lower_range = np.array([0, 0, 0])
        self.upper_range = np.array([179, 255, 255])
        self.stacked = None
        self.app = None
        self.existing_layers = {}
        for key in self._config.colors:
            self.existing_layers[key] = self._config.colors[key]

    def start(self):
        self.screen = Screen(self._config.general["monitor"])
        if self._config.advanced_options['graphic_debugger_layer_creator']:
            self.debugger_thread = threading.Thread(target=self.run_debugger_processor, daemon=False)
            self.debugger_thread.start()
            self.ui_thread = threading.Thread(target=self.run_debgger_ui, daemon=False)
            self.ui_thread.start()
            self.ui_lock = threading.Lock()
        else:
            self.item_finder = ItemFinder(self._config)
            self.template_finder = TemplateFinder(self.screen)
            self.debugger_thread = threading.Thread(target=self.run_old_debugger, daemon=False)
            self.debugger_thread.start()
        GraphicDebuggerController.is_running = True

    def stop(self):
        if self.debugger_thread: kill_thread(self.debugger_thread)
        if self.ui_thread: kill_thread(self.ui_thread)
        if self.app: self.app.destroy()
        cv2.destroyAllWindows()
        GraphicDebuggerController.is_running = False

    def update_text_box(self, new_value):
        self.current_layer_value_text = f"{self.h_l},{self.s_l},{self.v_l},{self.h_u},{self.s_u},{self.v_u}"

    def run_debgger_ui(self):
        self.app = tk.Tk()
        self.app.title("Graphic Debugger - Layer Creator")
        self.panel = None
        self.layers = tk.Listbox(self.app, width=60)

        # Slidebars
        self.slidebars_frame = tk.Frame(self.app)
        self.h_l = tk.IntVar(value=0)
        self.s_l = tk.IntVar(value=0)
        self.v_l = tk.IntVar(value=0)
        self.h_u = tk.IntVar(value=179)
        self.s_u = tk.IntVar(value=255)
        self.v_u = tk.IntVar(value=255)
        self.sliderbar_h_l = tk.Scale(self.slidebars_frame, label="H - Lower", from_=0, to=179, orient=tk.HORIZONTAL, length=255, variable=self.h_l, command=self.update_text_box)
        self.sliderbar_s_l = tk.Scale(self.slidebars_frame, label="S - Lower", from_=0, to=255, orient=tk.HORIZONTAL, length=255, variable=self.s_l, command=self.update_text_box)
        self.sliderbar_v_l = tk.Scale(self.slidebars_frame, label="V - Lower", from_=0, to=255, orient=tk.HORIZONTAL, length=255, variable=self.v_l, command=self.update_text_box)
        self.sliderbar_h_l.grid(column=0, row=0)
        self.sliderbar_s_l.grid(column=0, row=1)
        self.sliderbar_v_l.grid(column=0, row=2)
        self.sliderbar_h_u = tk.Scale(self.slidebars_frame, label="H - Upper", from_=0, to=179, orient=tk.HORIZONTAL, length=255, variable=self.h_u, command=self.update_text_box)
        self.sliderbar_s_u = tk.Scale(self.slidebars_frame, label="S - Upper", from_=0, to=255, orient=tk.HORIZONTAL, length=255, variable=self.s_u, command=self.update_text_box)
        self.sliderbar_v_u = tk.Scale(self.slidebars_frame, label="V - Upper", from_=0, to=255, orient=tk.HORIZONTAL, length=255, variable=self.v_u, command=self.update_text_box)
        self.sliderbar_h_u.grid(column=1, row=0)
        self.sliderbar_s_u.grid(column=1, row=1)
        self.sliderbar_v_u.grid(column=1, row=2)
        self.slidebars_frame.grid(column=0, row=0)
        self.current_layer_value_text = tk.Text(self.slidebars_frame)
        self.current_layer_value_text.grid(column=2, row=1)

        # Buttons
        self.buttons_frame = tk.Frame(self.app)
        self.display_only_current_layer = tk.IntVar(value=1)
        self.display_only_current_layer_button = tk.Checkbutton(self.buttons_frame, text="Display only the current layer", variable=self.display_only_current_layer)
        self.display_only_current_layer_button.grid(column=0, row=0)
        self.buttons_frame.grid(column=3, row=0)

        # Update layers
        c = 1
        for key in self.existing_layers:
            self.layers.insert(c, f"{key}")
        self.layers.grid(column=3, row=1, sticky=tk.N)
        self.app.mainloop()
        # cv2.namedWindow(self.window_name_trackbars)
        # cv2.namedWindow(self.window_name_images)
        # # Now create 6 trackbars that will control the lower and upper range of H,S and V channels.
        # # The Arguments are like this: Name of trackbar, window name, range,callback function. For Hue the range is 0-179 and for S,V its 0-255.
        # cv2.createTrackbar("H - Lower", self.window_name_trackbars, 0, 255, lambda x: None)
        # cv2.createTrackbar("S - Lower", self.window_name_trackbars, 0, 255, lambda x: None)
        # cv2.createTrackbar("V - Lower", self.window_name_trackbars, 0, 255, lambda x: None)
        # cv2.createTrackbar("H - Upper", self.window_name_trackbars, 255, 255, lambda x: None)
        # cv2.createTrackbar("S - Upper", self.window_name_trackbars, 255, 255, lambda x: None)
        # cv2.createTrackbar("V - Upper", self.window_name_trackbars, 255, 255, lambda x: None)
        # while True:
        #     # Get the new values of the trackbar in real time as the user changes them
        #     cv2.pollKey()  # This is needed only to keep the gui work as it handles the HighGUI events
        #     l_h = cv2.getTrackbarPos("H - Lower", self.window_name_trackbars)
        #     l_s = cv2.getTrackbarPos("S - Lower", self.window_name_trackbars)
        #     l_v = cv2.getTrackbarPos("V - Lower", self.window_name_trackbars)
        #     u_h = cv2.getTrackbarPos("H - Upper", self.window_name_trackbars)
        #     u_s = cv2.getTrackbarPos("S - Upper", self.window_name_trackbars)
        #     u_v = cv2.getTrackbarPos("V - Upper", self.window_name_trackbars)
        #     #self.ui_lock.acquire()
        #     self.lower_range = np.array([l_h, l_s, l_v])
        #     self.upper_range = np.array([u_h, u_s, u_v])
        #     # The debugger has processed some stuff, display it in a separate window
        #     if self.stacked is not None:
        #         cv2.imshow(self.window_name_images, self.stacked)
        #     #self.ui_lock.release()

    def _add_image(self, img):
        b, g, r = cv2.split(img)
        im = Image.fromarray(cv2.merge((r, g, b)))
        imgtk = ImageTk.PhotoImage(image=im)
        if self.panel is None:
            self.panel = tk.Label(self.app, image=imgtk)
            self.panel.image = imgtk
            self.panel.grid(column=0, columnspan=3, row=1)
        else:
            self.panel.configure(image=imgtk)
            self.panel.image = imgtk


    def run_debugger_processor(self):
        search_templates = ["A5_TOWN_0", "A5_TOWN_1", "A5_TOWN_2", "A5_TOWN_3"]
        # Create a window named trackbars.

        start_time = time.time()
        end_time = time.time()
        while 1:
            # Heavy processing ahead, don't do it at every loop
            if end_time - start_time < 0.75:
                end_time = time.time()
                continue
            start_time = time.time()

            img = self.screen.grab()
            # Convert the BGR image to HSV image.
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # Filter the image and get the binary mask
            #mask = cv2.inRange(hsv, self.lower_range, self.upper_range)
            # filters = [
            #     [np.array([17,109,97]),np.array([23,128,123])],
            #     [np.array([0,0,87]),np.array([64,24,111])],
            #     [np.array([95,42,135]),np.array([109,82,190])]
            # ]
            comb_img = np.zeros(img.shape, dtype="uint8")
            for name, layer in self.existing_layers.items():
                mask, filtered_img = color_filter(img, layer)
                comb_img = cv2.bitwise_or(filtered_img, comb_img)
            #filtered_img = cv2.bitwise_and(img, img, mask=mask)

            # Show item detections
            # combined_img = np.zeros(img.shape, dtype="uint8")
            # for key in self._config.colors:
            #     _, filterd_img = color_filter(img, self._config.colors[key])
            #     combined_img = cv2.bitwise_or(filterd_img, combined_img)
            # item_list = self.item_finder.search(img)
            # for item in item_list:
            #     cv2.circle(combined_img, item.center, 7, (0, 0, 255), 4)
            #     cv2.putText(combined_img, item.name, item.center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            # if len(item_list) > 0:
            #     print(item_list)
            # # Show Town A5 template matches
            # scores = {}
            # for template_name in search_templates:
            #     template_match = self.template_finder.search(template_name, img, threshold=0.65)
            #     if template_match.valid:
            #         scores[template_match.name] = template_match.score
            #         cv2.putText(combined_img, str(template_name), template_match.position, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            #         cv2.circle(combined_img, template_match.position, 7, (255, 0, 0), thickness=5)
            # if len(scores) > 0:
            #     print(scores)

            # stack the combined image and the filtered result
            #stacked = cv2.resize(np.hstack((combined_img, filtered_img)), None, fx=0.4, fy=0.4)
            #filtered_img
            # The processing was done in this thread, now pass it to the ui to display it on the window
            self.ui_lock.acquire()
            self._add_image(comb_img)
            self.stacked = comb_img
            self.ui_lock.release()
            end_time = time.time()

    def run_old_debugger(self):
        search_templates = ["A5_TOWN_0", "A5_TOWN_1", "A5_TOWN_2", "A5_TOWN_3"]
        while 1:
            img = self.screen.grab()
            # Show item detections
            combined_img = np.zeros(img.shape, dtype="uint8")
            for key in self._config.colors:
                _, filterd_img = color_filter(img, self._config.colors[key])
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
    # Create a window named trackbars.
    cv2.namedWindow("window_name")

    # Now create 6 trackbars that will control the lower and upper range of
    # H,S and V channels. The Arguments are like this: Name of trackbar,
    # window name, range,callback function. For Hue the range is 0-179 and
    # for S,V its 0-255.
    cv2.createTrackbar("H - Lower", "window_name", 0, 179, lambda x: None)
    cv2.createTrackbar("S - Lower", "window_name", 0, 255, lambda x: None)
    cv2.createTrackbar("V - Lower", "window_name", 0, 255, lambda x: None)
    cv2.createTrackbar("H - Upper", "window_name", 179, 179, lambda x: None)
    cv2.createTrackbar("S - Upper", "window_name", 255, 255, lambda x: None)
    cv2.createTrackbar("V - Upper", "window_name", 255, 255, lambda x: None)
    debugger = GraphicDebuggerController(Config())
    debugger.start()


