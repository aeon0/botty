import threading

import cv2
import numpy as np

from utils import mttkinter
from utils.misc import color_filter, kill_thread
from screen import Screen
from item import ItemFinder
from config import Config
import tkinter as tk
from template_finder import TemplateFinder
from PIL import ImageTk, Image
import re


class GraphicDebuggerController:
    """
    This class takes care of handling the window_name by starting and stopping it.

    The variable is_running is static and should be accessed only by the main thread or it is subject
    to race condition, if you plan to touch it from within a thread you might have to
    add a locking mechanism to order to access it.
    """
    window_name_trackbars = "Graphic Debugger - Trackbars"
    window_name_images = "Graphic Debugger - Images"

    def __init__(self):
        self._config = Config()
        self.screen = None
        self.item_finder = None
        self.template_finder = None
        self.debugger_thread = None
        self.ui_thread = None
        self.app = None
        self.existing_layers = {}
        for key in self._config.colors:
            self.existing_layers[key] = self._config.colors[key]
        self.active_layers = {}
        self.displayed_layers = {}
        self.panel = None
        self.is_running = False

    def start(self):
        self.screen = Screen()
        self.item_finder = ItemFinder()
        self.template_finder = TemplateFinder(self.screen)
        if self._config.advanced_options['graphic_debugger_layer_creator']:
            self.debugger_thread = threading.Thread(target=self.run_debugger_processor, daemon=False, name="Debugger-processor")
            self.debugger_thread.start()
            # we need to run the ui in the mainloop (tkinter kinda sucks)
            self.ui_thread = threading.Thread(target=self.run_debgger_ui, daemon=True, name="Debugger-ui")
            self.ui_thread.start()
        else:
            self.debugger_thread = threading.Thread(target=self.run_old_debugger, daemon=False, name="Debugger-processor")
            self.debugger_thread.start()
        self.is_running = True

    def stop(self):
        # TODO: these two layers variable (and panel) needs to be reassigned because F10 will not re-init the
        # controller, ideally these variables should be inherently part of the tkinter listboxes
        # as list variable and/or the debugger itself, as it is getting a bit more complicated
        # should probably be moved to a separate class and let the controller just take care of it
        # in the main thread
        if self._config.advanced_options['graphic_debugger_layer_creator']:
            self.active_layers = {}
            self.displayed_layers = {}
            self.panel = None
            self.app.destroy()
        if self.debugger_thread: kill_thread(self.debugger_thread)
        if self.ui_thread: kill_thread(self.ui_thread)
        cv2.destroyAllWindows()
        self.is_running = False

    def run_debgger_ui(self):
        self.app = mttkinter.Tk()
        self.app.title("Graphic Debugger - Layer Creator")
        self.app.protocol("WM_DELETE_WINDOW", self.app.iconify)

        ########### Variables ###########
        self.display_only_current_layer = tk.IntVar(value=0)
        self.item_finder_enabled = tk.IntVar(value=1)
        self.h_l = tk.IntVar(value=0)
        self.s_l = tk.IntVar(value=0)
        self.v_l = tk.IntVar(value=0)
        self.h_u = tk.IntVar(value=179)
        self.s_u = tk.IntVar(value=255)
        self.v_u = tk.IntVar(value=255)
        self.image_resize_ratio = tk.DoubleVar(value=0.5)

        ########### Slidebars ###########
        slidebars_frame = tk.Frame(self.app)
        sliderbar_h_l = tk.Scale(slidebars_frame, label="H - Lower", from_=0, to=179, orient=tk.HORIZONTAL, length=255, variable=self.h_l, command=self.update_text_box)
        sliderbar_h_l.grid(column=0, row=0)
        sliderbar_s_l = tk.Scale(slidebars_frame, label="S - Lower", from_=0, to=255, orient=tk.HORIZONTAL, length=255, variable=self.s_l, command=self.update_text_box)
        sliderbar_s_l.grid(column=0, row=1)
        sliderbar_v_l = tk.Scale(slidebars_frame, label="V - Lower", from_=0, to=255, orient=tk.HORIZONTAL, length=255, variable=self.v_l, command=self.update_text_box)
        sliderbar_v_l.grid(column=0, row=2)
        sliderbar_h_u = tk.Scale(slidebars_frame, label="H - Upper", from_=0, to=179, orient=tk.HORIZONTAL, length=255, variable=self.h_u, command=self.update_text_box)
        sliderbar_h_u.grid(column=1, row=0)
        sliderbar_s_u = tk.Scale(slidebars_frame, label="S - Upper", from_=0, to=255, orient=tk.HORIZONTAL, length=255, variable=self.s_u, command=self.update_text_box)
        sliderbar_s_u.grid(column=1, row=1)
        sliderbar_v_u = tk.Scale(slidebars_frame, label="V - Upper", from_=0, to=255, orient=tk.HORIZONTAL, length=255, variable=self.v_u, command=self.update_text_box)
        sliderbar_v_u.grid(column=1, row=2)
        slidebars_frame.grid(column=1, row=0, sticky=tk.W)

        # size slidebar
        frame = tk.Frame(self.app)
        frame.grid(column=0, row=0, sticky=tk.W)
        label = tk.Label(frame, textvariable=tk.StringVar(value="Image Size"))
        label.grid(column=0, row=0, sticky=tk.S)
        # 1.6 is the max value that the tool can be used in fullscreen with a 2560x1440 monitor
        slidebar_size = tk.Scale(frame, from_=1.6, to=0.4, orient=tk.VERTICAL, length=130, resolution=0.05, variable=self.image_resize_ratio)
        slidebar_size.grid(column=0, row=1, sticky=tk.N)

        ########### Buttons (Top right) ###########
        frame = tk.Frame(self.app)
        label = tk.Label(frame, textvariable=tk.StringVar(value="Current layer name:"))
        label.grid(column=0, row=0, sticky=tk.N+tk.W)
        self.current_layer_name_text = tk.Text(frame, height=1, width=25)
        self.current_layer_name_text.configure(state='normal')
        self.current_layer_name_text.insert(1.0, "my_layer_name")
        self.current_layer_name_text.grid(column=0, row=1, sticky=tk.N+tk.W)
        label = tk.Label(frame, textvariable=tk.StringVar(value="Current layer value: (you can copy this)"))
        label.grid(column=0, row=2, sticky=tk.N+tk.W)
        self.current_layer_value_text = tk.Text(frame, height=1, width=25)
        self.current_layer_value_text.configure(bg=self.app.cget('bg'), relief='flat')
        self.current_layer_value_text.configure(state='disabled')
        self.current_layer_value_text.grid(column=0, row=3, sticky=tk.N+tk.W)
        # Load
        load_layer_label = tk.Label(frame, textvariable=tk.StringVar(value="Load layer: (format: h_min,s_min,v_min,h_max,s_max,v_max)"))
        load_layer_label.grid(column=0, row=4, sticky=tk.N+tk.W)
        load_frame = tk.Frame(frame)
        self.load_layer_text = tk.Text(load_frame, height=1, width=25)
        self.load_layer_text.configure(state='normal')
        self.load_layer_text.grid(column=0, row=0, sticky=tk.W)
        load_button = tk.Button(load_frame, text='Load', command=self.load_layer)
        load_button.grid(column=0, row=1, sticky=tk.W)
        load_frame.grid(column=0, row=5, sticky=tk.N+tk.W)
        button = tk.Button(frame, text="Add current layer to active", command=self.add_current_layer_to_active)
        button.grid(column=0, row=6, sticky=tk.N+tk.W)
        display_only_current_layer_button = tk.Checkbutton(
            frame,
            text="Filter with the current layer only",
            variable=self.display_only_current_layer,
            command=self.update_displayed_layers)
        display_only_current_layer_button.grid(column=0, row=7, sticky=tk.N+tk.W)
        enable_item_finder_button = tk.Checkbutton(
            frame,
            text="Enable Item Finder (performance will be impacted)",
            variable=self.item_finder_enabled)
        enable_item_finder_button.grid(column=0, row=8, sticky=tk.N+tk.W)
        self.update_text_box()
        frame.grid(column=3, row=0)

        ########### Layers Display (2 listboxes + buttons) ###########
        all_layers_frame = tk.Frame(self.app)
        all_layers_frame.grid(column=3, row=1, sticky=tk.N)
        # active
        self.layers_active_listbox = tk.Listbox(all_layers_frame, width=25, height=20, selectmode=tk.EXTENDED)
        self.layers_active_listbox.grid(column=0, row=1, sticky=tk.N)
        active_layers_label_frame = tk.Frame(all_layers_frame)
        layers_active_label = tk.Label(active_layers_label_frame, textvariable=tk.StringVar(value="Active Layers"))
        layers_active_label.grid(column=0, row=0)
        remove_layer = tk.Button(active_layers_label_frame, text='Remove Selected', command=self.remove_selected_active_layer)
        remove_layer.grid(column=1, row=0)
        active_layers_label_frame.grid(column=0, row=0, sticky=tk.N)
        # existing (from config)
        self.layers_existing_listbox = tk.Listbox(all_layers_frame, width=25, height=20, selectmode=tk.EXTENDED)
        for key in self.existing_layers:
            self.layers_existing_listbox.insert(1, f"{key}")
        self.layers_existing_listbox.grid(column=2, row=1, sticky=tk.N)
        layers_existing_label = tk.Label(all_layers_frame, textvariable=tk.StringVar(value="Existing Layers"))
        layers_existing_label.grid(column=2, row=0, sticky=tk.N)
        # buttons to add(/all) layers from active list
        layers_button_frame = tk.Frame(all_layers_frame)
        add_all_existing_layers_button = tk.Button(layers_button_frame, text='<<', command=self.add_all_existing_layers)
        add_all_existing_layers_button.grid(column=0, row=0)
        add_selected_existing_layer_button = tk.Button(layers_button_frame, text=' < ', command=self.add_selected_existing_layer)
        add_selected_existing_layer_button.grid(column=0, row=1)
        layers_button_frame.grid(column=1, row=1)
        # display active layers in an easy to copy way:
        self.active_layers_values_text = tk.Text(all_layers_frame, height=20, width=50)
        self.active_layers_values_text.configure(bg=self.app.cget('bg'), relief='flat')
        self.active_layers_values_text.configure(state='disabled')
        self.active_layers_values_text.grid(column=0, columnspan=3, row=2)

        # keep previous debugger logic in place by default all existing layers
        self.add_all_existing_layers()
        self.app.mainloop()

    def update_text_box(self, new_value=None):
        self.current_layer_value_text.configure(state='normal')
        self.current_layer_value_text.delete(1.0, tk.END)
        self.current_layer_value_text.insert(1.0, f"{self.h_l.get()},{self.s_l.get()},{self.v_l.get()},{self.h_u.get()},{self.s_u.get()},{self.v_u.get()}")
        self.current_layer_value_text.configure(state='disabled')

        self.current_layer = [np.array([self.h_l.get(), self.s_l.get(), self.v_l.get()]), np.array([self.h_u.get(), self.s_u.get(), self.v_u.get()])]
        self.update_displayed_layers()

    def add_all_existing_layers(self):
        for key, value in self.existing_layers.items():
            self._add_layer_to_active(key, value)

    def add_selected_existing_layer(self):
        current_selection = [self.layers_existing_listbox.get(i) for i in self.layers_existing_listbox.curselection()]
        for key, value in self.existing_layers.items():
            if key in current_selection:
                self._add_layer_to_active(key, value)

    def remove_selected_active_layer(self):
        current_selection = [[i, self.layers_active_listbox.get(i)] for i in self.layers_active_listbox.curselection()]
        for e in reversed(current_selection):
            self.active_layers.pop(e[1])
            self.layers_active_listbox.delete(e[0])
        self.update_displayed_layers()
        self._update_active_layers_text_box()

    def add_current_layer_to_active(self):
        name = self.current_layer_name_text.get(1.0, tk.END).strip()
        self._add_layer_to_active(name, self.current_layer)

    def update_displayed_layers(self):
        if self.display_only_current_layer.get():
            self.displayed_layers = {}
            self.displayed_layers[self.current_layer_name_text.get(1.0, tk.END)] = self.current_layer
        else:
            self.displayed_layers = {}
            for key, value in self.active_layers.items():
                self.displayed_layers[key] = value

    def load_layer(self):
        string_value = self.load_layer_text.get(1.0, tk.END).strip()
        pattern = re.compile("^\d{0,3},\d{0,3},\d{0,3},\d{0,3},\d{0,3},\d{0,3}$")
        match = bool(re.match(pattern, string_value))
        if match:
            values = string_value.split(',')
            self.h_l.set(values[0])
            self.s_l.set(values[1])
            self.v_l.set(values[2])
            self.h_u.set(values[3])
            self.s_u.set(values[4])
            self.v_u.set(values[5])
        else:
            print('String in the wrong format, it should match this regex: ^\\d{0,3},\\d{0,3},\\d{0,3},\\d{0,3},\\d{0,3},\\d{0,3}$')
        self.update_text_box()

    def _add_layer_to_active(self, layer_name, layer_value):
        if layer_name not in self.active_layers:
            self.active_layers[layer_name] = layer_value
            self.layers_active_listbox.insert(1, layer_name)
            self.update_displayed_layers()
        else:
            print(f'Add layer failed, layer {layer_name} already active')
        self._update_active_layers_text_box()

    def _update_active_layers_text_box(self):
        self.active_layers_values_text.configure(state='normal')
        self.active_layers_values_text.delete(1.0, tk.END)
        string_value = ''
        for key, value in self.active_layers.items():
            string_value += key
            concatenated_value = ','.join([str(e) for e in value[0]] + [str(e) for e in value[1]])
            #concatenated_value = np.concatenate((value[0], value[1]))
            string_value += ','.join(concatenated_value)
            string_value += '\n'
        #self.active_layers_values_text.insert(1.0, string_value)
        self.active_layers_values_text.insert(1.0, '\n'.join(f"{key}={','.join([str(e) for e in value[0]] + [str(e) for e in value[1]])}" for key, value in self.active_layers.items()))
        self.active_layers_values_text.configure(state='disabled')

    def add_image(self, img):
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
        while 1:
            img = self.screen.grab()
            # Convert the BGR image to HSV image.
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            combined_img = np.zeros(img.shape, dtype="uint8")
            for name, layer in self.displayed_layers.items():
                mask, filtered_img = color_filter(img, layer)
                combined_img = cv2.bitwise_or(filtered_img, combined_img)

            # Show item detections
            if self.item_finder_enabled.get():
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
                        cv2.putText(combined_img, str(template_name), template_match.center, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        cv2.circle(combined_img, template_match.center, 7, (255, 0, 0), thickness=5)
                if len(scores) > 0:
                    print(scores)

            if self.image_resize_ratio.get() != 1:
                combined_img = cv2.resize(combined_img, None, fx=self.image_resize_ratio.get(), fy=self.image_resize_ratio.get())
            # The processing was done in this thread, now pass it to the ui to display it on the window
            self.add_image(combined_img)

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
                    cv2.putText(combined_img, str(template_name), template_match.center, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.circle(combined_img, template_match.center, 7, (255, 0, 0), thickness=5)
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
