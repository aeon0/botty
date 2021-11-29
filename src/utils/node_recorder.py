from screen import Screen
import cv2
from config import Config
from template_finder import TemplateFinder
from utils.misc import load_template
import mouse
import keyboard
import os


class NodeRecorder:
    def __init__(self, screen: Screen, run_name):
        #TODO: Remove generated folder
        os.system("mkdir generated")
        os.system(f"cd generated && mkdir templates && cd templates && mkdir {run_name} && cd {run_name} && mkdir nodes")
        self._run_name = run_name
        self._template_counter = 0
        self._half_width = 1920//2
        self._half_height = 1080//2
        self._screen = screen
        self._node = None
        self._ref_points = {}
        self._curr_state = 0
        self._idx = 0
        self._upper_left = None
        self._template_finder = TemplateFinder(self._screen, 1.0)
        self._template_finder._templates = {}
        self._pather_code_file = "generated/pather_generated.py"
        self._template_code_file = "generated/template_finder_generated.py"
        print("0 - Select Node: move to new node and press f8")

    def find_previous_templates(self):
        img = self._screen.grab()
        for key in self._template_finder._templates:
            if key not in self._ref_points:
                found, pos = self._template_finder.search(key, img)
                if found:
                    print(f"Found Previous: {key}")
                    self._ref_points[key] = pos

    def hook(self, e):
        if e.event_type == "down":
            if e.name == "f12":
                os._exit(1)
            img = self._screen.grab()
            if e.name == "f8" and (self._curr_state == 0 or self._curr_state == 1):
                loc_monitor = mouse.get_position()
                loc_screen = self._screen.convert_monitor_to_screen(loc_monitor)
                if self._curr_state == 0:
                    self._node = (self._half_width, self._half_height)
                    self.find_previous_templates()
                    self._curr_state = 1
                    print("1 - Select Ref Point: move mouse to upper-left corner and press f8, or press f7 to move to next node")
                elif self._curr_state == 1:
                    if self._upper_left is None:
                        self._upper_left = loc_screen
                        print("2 - Select bottom-right corner and press f8")
                    else:
                        center = ((loc_screen[0] + self._upper_left[0]) // 2, (loc_screen[1] + self._upper_left[1]) // 2)
                        delta_x = (loc_screen[0] - self._upper_left[0]) // 2
                        delta_y = (loc_screen[1] - self._upper_left[1]) // 2
                        ref_point_name = f"{self._run_name}_{self._template_counter}"
                        self._template_counter += 1
                        print(f"3 - Create ref point {ref_point_name}")
                        self._ref_points[ref_point_name] = center
                        # write template code
                        code = f'"{ref_point_name.upper()}": [load_template("assets/templates/{self._run_name}/{ref_point_name}.png", self._scale_factor), self._scale_factor],'
                        f = open(self._template_code_file, 'a+')
                        f.write(code + "\n")
                        f.close()
                        # save as png
                        template_img = img[center[1]-delta_y:center[1]+delta_y, center[0]-delta_x:center[0]+delta_x]
                        cv2.imwrite(f"generated/templates/{self._run_name}/{ref_point_name}.png", template_img)
                        self._upper_left = None
                        self._lock_templates = True
                        self._template_finder._templates[ref_point_name] = [cv2.resize(template_img, None, fx=self._template_finder._scale_factor, fy=self._template_finder._scale_factor, interpolation=cv2.INTER_NEAREST), self._template_finder._scale_factor]
                        self._lock_templates = False
                        print("1 - Select Ref Point: move to new node and press f8, or press f7 to move to next node")
            if e.name == "f7" and self._curr_state == 1:
                # save node with index as img
                img_view = img[:, :, :]
                cv2.circle(img_view, self._node, 6, (0, 0, 255), 3)
                for key in self._ref_points:
                    cv2.circle(img_view, self._ref_points[key], 6, (0, 255, 0), 3)
                img_view = cv2.resize(img_view, None, fx=0.5, fy=0.5)
                node_name = f"{self._run_name}_{self._idx}"
                cv2.imwrite(f"generated/templates/{self._run_name}/nodes/{node_name}.png", img_view)
                # write pather code
                code = f"{self._idx}: " + "{"
                for key in self._ref_points:
                    rel_loc = (self._node[0] - self._ref_points[key][0], self._node[1] - self._ref_points[key][1])
                    code += f'"{key.upper()}": {rel_loc}, '
                code = code[:-2] + "},"
                self._idx += 1
                f = open(self._pather_code_file, 'a+')
                f.write(code + "\n")
                f.close()
                self._node = None
                self._ref_points = {}
                self._curr_state = 0
                print("0 - Select Node: move mouse to spot you want to walk to and press f8")


if __name__ == "__main__":
    keyboard.add_hotkey('f12', lambda: print('Force Exit (f12)') or os._exit(1))
    print("Enter run name...")
    run_name = input()

    config = Config()
    screen = Screen(config.general["monitor"])
    scale = 0.5

    recorder = NodeRecorder(screen, run_name)
    keyboard.hook(recorder.hook, suppress=True)

    while 1:
        img = screen.grab()
        if recorder._node is not None:
            cv2.circle(img, recorder._node, 10, (0, 0, 255), 5)
        for key in recorder._ref_points:
            cv2.circle(img, recorder._ref_points[key], 10, (0, 255, 0), 5)
        img_scaled = cv2.resize(img, None, fx=scale, fy=scale)
        cv2.imshow("vis", img_scaled)
        cv2.waitKey(1)
