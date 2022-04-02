import abc
import shop.shop_helpers
import time
import glob
import os
import math
from shop.shop_helpers import Coordinate
from config import Config
from typing import Dict, Tuple, Union, List, Callable
from screen import grab, convert_screen_to_monitor, convert_screen_to_abs, convert_abs_to_monitor, convert_monitor_to_screen
from utils.custom_mouse import mouse
from utils.misc import wait
from template_finder import TemplateFinder
from logger import Logger


class ShopperBase(abc.ABC):

    @abc.abstractmethod
    def get_name(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass

    def __init__(self):
        self.run_count = 0
        self.start_time = time.time()
        self.roi_vendor = Config().ui_roi["left_inventory"]
        self.rx, self.ry, _, _ = self.roi_vendor
        self.first_tab_x, self.second_tab_y = convert_screen_to_monitor((115, 77))
        self.second_tab_x, self.second_tab_y = convert_screen_to_monitor((180, 77))
        self.third_tab_x, self.third_tab_y = convert_screen_to_monitor((245, 77))
        self.c_x, self.c_y = convert_screen_to_monitor((Config().ui_pos["center_x"], Config().ui_pos["center_y"]))
        self.speed_factor = self.get_effective_faster_run_walk()
        self.apply_pather_adjustment = Config().shop["apply_pather_adjustment"]
        self.search_tabs = set([])
        self.roi_item_stats = [0, 0, int(math.ceil(Config().ui_pos["screen_width"] // 2)), int(math.ceil(Config().ui_pos["screen_height"] - 100))]
        self.template_stat_assets = self.get_stat_template_assets()
        self.debug_stats_count = {}

    def click_tab(self, tab_index=0):
        if tab_index == 1:
            self.click_first_tab()
        elif tab_index == 2:
            self.click_second_tab()
        elif tab_index == 3:
            self.click_third_tab()
        else:
            return

    def click_first_tab(self):
        mouse.move(self.second_tab_x, self.second_tab_y, randomize=3, delay_factor=[0.6, 0.8])
        wait(0.05, 0.1)
        mouse.press(button="left")
        wait(0.3, 0.4)

    def click_second_tab(self):
        mouse.move(self.second_tab_x, self.second_tab_y, randomize=3, delay_factor=[0.6, 0.8])
        wait(0.05, 0.1)
        mouse.press(button="left")
        wait(0.3, 0.4)

    def click_third_tab(self):
        mouse.move(self.third_tab_x, self.third_tab_y, randomize=3, delay_factor=[0.6, 0.8])
        wait(0.05, 0.1)
        mouse.press(button="left")
        wait(0.3, 0.4)

    @staticmethod
    def mouse_over(pos: Coordinate()):
        """
        Moves the mouse over a given position coordinate
        """
        mouse.move(pos.x, pos.y, randomize=3, delay_factor=[0.5, 0.6])
        #wait(0.05, 0.1)

    @staticmethod
    def get_stat_template_assets():
        assets = []
        cleaned_assets = []
        assets.extend(glob.glob('./assets/shop/other/[0-9]*.png'))
        assets.extend(glob.glob('./assets/shop/other/level*.png'))
        assets.extend(glob.glob('./assets/shop/other/suffix*.png'))
        for asset in assets:
            head, tail = os.path.split(asset)
            asset_name = tail.split('.')[0].upper()
            cleaned_assets.append(asset_name)
        return cleaned_assets

    @staticmethod
    def get_effective_faster_run_walk():
        """
        Faster run walk is not linear and diminishing returns should be calculated
        """
        speed = Config().shop["faster_run_walk"]
        if speed < 1:
            speed = 1.0
        else:
            speed = round((((150 * speed) / (150 + speed)) / 100.0), 2)
        Logger.debug(f"Effective Run Walk Factor: {speed * 100}%")
        return speed

    def move_shopper(self, x, y, duration):
        """
        Moves the shopper
        """
        pos_m = convert_abs_to_monitor((x, y))
        mouse.move(pos_m[0], pos_m[1])
        self.hold_move(pos_m, time_held=(duration * self.speed_factor))

    def check_stats(self, img):
        t = time.perf_counter()
        stat_count = 0
        for stat_asset in self.template_stat_assets:
            template_match = TemplateFinder(True).search(stat_asset, img, roi=self.roi_item_stats, threshold=0.97)
            if template_match.valid:
                stat_count += 1
                Logger.debug(f"Stat identified: {stat_asset} Score: {template_match.score}")
                if not self.debug_stats_count.get(stat_asset):
                    self.debug_stats_count[stat_asset] = 1
                else:
                    self.debug_stats_count[stat_asset] += 1
        t = time.perf_counter() - t
        Logger.debug(f"{stat_count} stats identified in {t:0.4f} seconds")

    # A variation of the move() function from pather.py
    def hold_move(self, pos_monitor: Tuple[float, float], time_held: float = 2.0):
        factor = Config().advanced_options["pathing_delay_factor"]
        # in case we want to walk we actually want to move a bit before the point cause d2r will always "overwalk"
        pos_screen = convert_monitor_to_screen(pos_monitor)
        pos_abs = convert_screen_to_abs(pos_screen)

        # This logic (from pather.py) sometimes negatively affects the shopper, so default is to skip this.
        if self.apply_pather_adjustment:
            dist = math.dist(pos_abs, (0, 0))
            min_wd = Config().ui_pos["min_walk_dist"]
            max_wd = random.randint(int(Config().ui_pos["max_walk_dist"] * 0.65), Config().ui_pos["max_walk_dist"])
            adjust_factor = max(max_wd, min(min_wd, dist - 50)) / dist
            pos_abs = [int(pos_abs[0] * adjust_factor), int(pos_abs[1] * adjust_factor)]

        x, y = convert_abs_to_monitor(pos_abs)
        mouse.move(x, y, randomize=5, delay_factor=[factor * 0.1, factor * 0.14])
        wait(0.012, 0.02)
        mouse.press(button="left")
        wait(time_held - 0.05, time_held + 0.05)
        mouse.release(button="left")


ShopperBase.register(tuple)

assert issubclass(tuple, ShopperBase)
assert isinstance((), ShopperBase)
