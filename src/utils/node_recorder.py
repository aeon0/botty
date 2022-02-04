from screen import Screen
import cv2
from config import Config
from template_finder import TemplateFinder
from utils.misc import load_template, cut_roi
import mouse
import keyboard
import os
import shutil
from pathlib import Path
from typing import Tuple
import math


class NodeRecorder:
    def __init__(self, screen: Screen, config: Config, run_name):
        if os.path.exists("generated"):
            for path in Path("generated").glob("**/*"):
                if path.is_file():
                    os.remove(path)
                elif path.is_dir():
                    shutil.rmtree(path)
            shutil.rmtree("generated")
        os.system("mkdir generated")
        os.system(f"cd generated && mkdir templates && cd templates && mkdir {run_name} && cd {run_name} && mkdir nodes")
        self._run_name = run_name
        self._offset = 100
        self._template_counter = 0
        self._half_width = config.ui_pos["screen_width"] // 2
        self._half_height = config.ui_pos["screen_height"] // 2
        self._screen = screen
        self._curr_state = 0
        self._upper_left = None
        self._template_finder = TemplateFinder(self._screen)
        self._template_finder._templates = {}
        self._pather_code_file = "generated/pather_generated.py"
        self.ref_points = {}
        self.nodes = {}
        self.debug_node_pos = {}
        # Starting with template recording:
        print("1 - Select top-left corner and press f8")

    @staticmethod
    def _convert_rel_to_abs(rel_loc: Tuple[float, float], pos_abs: Tuple[float, float]) -> Tuple[float, float]:
        return (rel_loc[0] + pos_abs[0], rel_loc[1] + pos_abs[1])

    def find_templates(self, img):
        ref_points = {}
        for key in self._template_finder._templates:
            found = self._template_finder.search(key, img, use_grayscale=False, threshold=0.77)
            if found.valid:
                ref_points[key] = found.center
        return ref_points

    def hook(self, e):
        if e.event_type == "down":
            if e.name == "f12":
                os._exit(1)
            self.ref_points = {}
            self.debug_node_pos = {}
            img = self._screen.grab()
            loc_monitor = mouse.get_position()
            loc_screen = self._screen.convert_monitor_to_screen(loc_monitor)
            if e.name == "f8" and self._curr_state == 0:
                # create a tempalte
                if self._upper_left is None:
                    self._upper_left = loc_screen
                    print("-- Select bottom-right corner and press f8")
                    return
                else:
                    bottom_right = loc_screen
                    width = (bottom_right[0] - self._upper_left[0])
                    height = (bottom_right[1] - self._upper_left[1])
                    ref_point_name = f"{self._run_name}_{self._template_counter}"
                    self._template_counter += 1
                    # save as png
                    template_img = cut_roi(img, [*self._upper_left, width, height])
                    template_path = f"generated/templates/{self._run_name}/{ref_point_name}.png"
                    cv2.imwrite(template_path, template_img)
                    self._upper_left = None
                    template_img = load_template(template_path, 1.0, False)
                    self._template_finder._templates[ref_point_name] = [template_img, cv2.cvtColor(template_img, cv2.COLOR_BGRA2GRAY), 1.0, None]
            elif e.name == "f7":
                self.ref_points = {}
            else:
                self.ref_points = self.find_templates(img)

            if e.name == "f9":
                # add current loc screen as node
                new_node_idx = self._offset + len(self.nodes)
                self.nodes[new_node_idx] = {}
                for key in self.ref_points:
                    rel_loc = (loc_screen[0] - self.ref_points[key][0], loc_screen[1] - self.ref_points[key][1])
                    self.nodes[new_node_idx][key] = rel_loc

            if e.name == "f10" or e.name == "f9" and self.ref_points is not None:
                # find all nodes:
                for node_idx in self.nodes:
                    # try to find the screen coordinate of the node
                    node_screen_pos = None
                    for template_key in self.nodes[node_idx]:
                        if template_key in self.ref_points:
                            ref_pos_screen = self.ref_points[template_key]
                            # Get reference position of template in abs coordinates
                            ref_pos_abs = self._screen.convert_screen_to_abs(ref_pos_screen)
                            # Calc the abs node position with the relative coordinates (relative to ref)
                            node_pos_rel = self.nodes[node_idx][template_key]
                            node_pos_abs = self._convert_rel_to_abs(node_pos_rel, ref_pos_abs)
                            node_screen_pos = self._screen.convert_abs_to_screen(node_pos_abs)
                            self.debug_node_pos[node_idx] = node_screen_pos
                            break
                    # if it was found try to add all other visible templates to it that are not already included
                    if node_screen_pos is not None:
                        for template_key in self.ref_points:
                            if template_key not in self.nodes[node_idx]:
                                rel_loc = (node_screen_pos[0] - self.ref_points[template_key][0], node_screen_pos[1] - self.ref_points[template_key][1])
                                self.nodes[node_idx][template_key] = rel_loc
                # print info to console and write code
                f = open(self._pather_code_file, 'w')
                print("---- Current Recorded Nodes: ----")
                for k in self.nodes:
                    print(self.nodes[k])
                    new_path = []
                    for template in self.nodes[k]:
                        dist = math.dist((0, 0), self.nodes[k][template])
                        new_path.append({"key": template, "pos": self.nodes[k][template], "dist": dist})
                    results = sorted(new_path, key=lambda r: r["dist"])
                    code = f"{k}: " + "{"
                    for i, res in enumerate(results):
                        if res["dist"] < 1100 and i < 8:
                            code += f'"{res["key"].upper()}": {res["pos"]}, '
                    f.write(code + "}\n")
                f.close()
                print("")
            print("f8: Create Template | f9: New node at cursor | f10: update nodes with visible templates")

if __name__ == "__main__":
    keyboard.add_hotkey('f12', lambda: print('Force Exit (f12)') or os._exit(1))
    print("Enter run name...")
    run_name = input()

    config = Config()
    screen = Screen()

    recorder = NodeRecorder(screen, config, run_name)
    keyboard.hook(recorder.hook, suppress=True)

    while 1:
        img = screen.grab().copy()
        try:
            for key in recorder.debug_node_pos:
                cv2.circle(img, recorder.debug_node_pos[key], 8, (0, 0, 255), 4)
                cv2.putText(img, str(key), recorder.debug_node_pos[key], cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            for key in recorder.ref_points:
                cv2.circle(img, recorder.ref_points[key], 8, (0, 255, 0), 4)
                cv2.putText(img, key, recorder.ref_points[key], cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        except Exception:
            pass
        img = cv2.resize(img, None, fx=0.5, fy=0.5)
        cv2.imshow("vis", img)
        cv2.waitKey(1)
