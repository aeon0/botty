import abc
import shop.shop_helpers
import time
import glob
import os
import math
import cv2
from shop.shop_helpers import Coordinate
from config import Config
from typing import Dict, Tuple, Union, List, Callable
from screen import grab, convert_screen_to_monitor, convert_screen_to_abs, convert_abs_to_monitor, convert_monitor_to_screen
from utils.custom_mouse import mouse
from utils.misc import wait
from template_finder import TemplateFinder
from logger import Logger
from utils.restart import kill_game


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
        self.first_tab_x, self.first_tab_y = convert_screen_to_monitor((115, 77))
        self.second_tab_x, self.second_tab_y = convert_screen_to_monitor((180, 77))
        self.third_tab_x, self.third_tab_y = convert_screen_to_monitor((245, 77))
        self.fourth_tab_x, self.fourth_tab_y = convert_screen_to_monitor((330, 77))
        self.c_x, self.c_y = convert_screen_to_monitor((Config().ui_pos["center_x"], Config().ui_pos["center_y"]))
        self.speed_factor = self.get_effective_faster_run_walk()
        self.apply_pather_adjustment = Config().shop["apply_pather_adjustment"]
        self.search_tabs = set([])
        self.roi_item_stats = [0, 0, int(math.ceil(Config().ui_pos["screen_width"] // 2)), int(math.ceil(Config().ui_pos["screen_height"] - 100))]
        self.template_stat_assets = self.get_stat_template_assets()
        self.debug_stats_count = {}
        self.debug_stat_checks = Config().shop["debug_stat_checks"]
        self.max_game_time = Config().shop["max_game_time"]
        self.items_bought = {}
        pos_m = convert_abs_to_monitor((-200, 0))
        self.mouse_reset = Coordinate(pos_m[0], pos_m[1])
        self.trade_roi = [0, 520, 500, 200]

    def get_time(self):
        return round(time.time() - self.start_time)

    def check_run_time(self):
        Logger.debug(f"Time: {self.get_time()}, Max Time: {self.max_game_time}")
        if self.get_time() > self.max_game_time:
            Logger.debug(f"Max game time {self.max_game_time} reached. Quitting.")
            kill_game()
            os._exit(1)

    def click_tab(self, tab_index=0):
        if tab_index == 1:
            mouse.move(self.first_tab_x, self.first_tab_y, randomize=3, delay_factor=[0.6, 0.8])
        elif tab_index == 2:
            mouse.move(self.second_tab_x, self.second_tab_y, randomize=3, delay_factor=[0.6, 0.8])
        elif tab_index == 3:
            mouse.move(self.third_tab_x, self.third_tab_y, randomize=3, delay_factor=[0.6, 0.8])
        elif tab_index == 4:
            mouse.move(self.fourth_tab_x, self.fourth_tab_y, randomize=3, delay_factor=[0.6, 0.8])
        else:
            return
        wait(0.05, 0.1)
        mouse.press(button="left")
        wait(0.3, 0.4)

    @staticmethod
    def mouse_over(pos: Coordinate(0, 0)):
        """
        Moves the mouse over a given position coordinate
        """
        mouse.move(pos.x, pos.y, randomize=3, delay_factor=[0.5, 0.6])
        wait(0.05, 0.1)

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
        speed = round(((150 * speed) / (150 + speed)), 2)
        Logger.debug(f"Effective Run Walk Factor: {speed}%")
        return round((speed + 100) / 100.0, 2)

    def move_shopper(self, x, y, duration):
        """
        Moves the shopper
        """
        pos_m = convert_abs_to_monitor((x, y))
        mouse.move(pos_m[0], pos_m[1])
        self.hold_move(pos_m, time_held=(duration / self.speed_factor))

    def check_stats(self, img):
        if not self.debug_stat_checks:
            return
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
        wait(time_held, time_held + 0.05)
        mouse.release(button="left")

    def buy_item(self, item_name):
        if Config().shop["max_single_item_shop_quantity"] and self.items_bought.get(item_name):
            # Item already purchased
            Logger.debug(f"Found {item_name} but skipping because already purchased and max_single_item_shop_quantity is set to true in shop config")
            return
        mouse.click(button="right")
        if not self.items_bought.get(item_name):
            self.items_bought[item_name] = 1
        else:
            self.items_bought[item_name] += 1
        Logger.debug(f"Bought {item_name} number {self.items_bought[item_name]}!")
        if Config().shop["max_item_shop_quantity"]:
            Logger.debug("Wrapping up shopping because item was bought and max_item_shop_quantity is set to true in shop config")
            ShopperBase.stop_shopping()

    @staticmethod
    def stop_shopping():
        os._exit(0)

    def search_for_staff_of_teleportation(self):
        if self.look_for_staff_of_teleportation:
            self.search_for_item(
                item_description="staff_of_teleportation",
                item_type_asset_keys=["BATTLE_STAFF",
                 "WAR_STAFF", "GNARLED_STAFF"],
                item_stat_asset_keys_required=["SUFFIX_OF_TELEPORTATION"])

    def search_for_wand_of_life_tap(self):
        if self.look_for_wand_of_life_tap:
            self.search_for_item(
                item_description="wand_of_life_tap",
                item_type_asset_keys=["BONE_WAND",
                 "GRIM_WAND", "YEW_WAND", "WAND"],
                item_stat_asset_keys_required=["SUFFIX_OF_LIFE_TAP"])

    def search_for_wand_of_lower_resist(self):
        if self.look_for_wand_of_lower_resist:
            self.search_for_item(
                item_description="wand_of_lower_resist",
                item_type_asset_keys=["BONE_WAND",
                 "GRIM_WAND", "YEW_WAND", "WAND"],
                item_stat_asset_keys_required=["SUFFIX_OF_LOWER_RESIST"])

    def search_for_leaf_runeword_base(self):
        if self.look_for_leaf_runeword_base:
            self.search_for_item(
                item_description="leaf_runeword_base",
                item_type_asset_keys=["SHORT_STAFF", "LONG_STAFF", "GNARLED_STAFF", "BATTLE_STAFF"],
                item_type_asset_threshold=0.8,
                item_stat_asset_keys_required=["2_SOCKETED"],
                item_stat_asset_keys_avoid=["PREFIX_MECHANICS"],
                item_misc_stat_asset_keys=["3_TO_ENCHANT", "3_TO_FIRE_BALL", "3_TO_FIRE_WALL", "3_TO_STATIC_FIELD", "3_TO_WARMTH", "3_TO_FIRE_BOLT", "3_TO_METEOR"],
                min_misc_stats=2,
                item_stat_asset_threshold=0.96)

    def search_for_warcry_weapon(self):
        if self.look_for_warcry_weapon:
            self.search_for_item(
                item_description="warcry_weapon",
                item_type_asset_keys=["GREAT_SWORD", "WAR_AXE", "FLAMBERGE", "WAR_SWORD", "GREAT_SWORD", "BASTARD_SWORD", "CRYSTAL_SWORD"],
                item_stat_asset_keys_required=["PREFIX_ECHOING"]
            )

    def search_for_warcry_stick(self):
        if self.look_for_warcry_stick:
            self.search_for_item(
                item_description="warcry_stick",
                item_type_asset_keys=["GLAIVE", "THROWING_SPEAR"],
                item_stat_asset_keys_required=["PREFIX_ECHOING"]
            )

    def search_for_jewelers_armor_of_the_whale(self):
        if self.look_for_jewelers_armor_of_the_whale:
            self.search_for_item(
                item_description="jewelers_armor_of_the_whale",
                item_type_asset_keys=["FIELD_PLATE", "PLATE_MAIL", "GOTHIC_PLATE", "FULL_PLATE_MAIL", "ANCIENT_ARMOR", "LIGHT_PLATE"],
                item_stat_asset_keys_required=["PREFIX_JEWELERS"],
                item_misc_stat_asset_keys=["SUFFIX_OF_THE_WHALE"],
                min_misc_stats=1
            )

    def search_for_resist_belt_of_the_whale(self):
        if self.look_for_resist_belt_of_the_whale:
            self.search_for_item(
                item_description="resist_belt_of_the_whale",
                item_type_asset_keys=["PLATED_BELT"],
                item_stat_asset_keys_required=["SUFFIX_OF_THE_WHALE"],
                item_misc_stat_asset_keys=["PREFIX_COBALT", "PREFIX_CORAL", "PREFIX_GARNET"],
                min_misc_stats=1
            )

    def search_for_resist_belt_of_wealth(self):
        if self.look_for_resist_belt_of_wealth:
            self.search_for_item(
                item_description="resist_belt_of_wealth",
                item_type_asset_keys=["PLATED_BELT"],
                item_stat_asset_keys_required=["SUFFIX_OF_WEALTH"],
                item_misc_stat_asset_keys=["PREFIX_COBALT", "PREFIX_CORAL", "PREFIX_GARNET"],
                min_misc_stats=1
            )

    def search_for_artisans_helm_of_the_whale(self):
        if self.look_for_artisans_helm_of_the_whale:
            self.search_for_item(
                item_description="artisans_helm_of_the_whale",
                item_type_asset_keys=["CROWN", "GREAT_HELM", "BONE_HELM"],
                item_stat_asset_keys_required=["PREFIX_ARTISANS"],
                item_misc_stat_asset_keys=["SUFFIX_OF_THE_WHALE"],
                min_misc_stats=1
            )

    def search_for_artisans_helm_of_stability(self):
        if self.look_for_artisans_helm_of_stability:
            self.search_for_item(
                item_description="artisans_helm_of_stability",
                item_type_asset_keys=["CROWN", "GREAT_HELM", "BONE_HELM"],
                item_stat_asset_keys_required=["PREFIX_ARTISANS"],
                item_misc_stat_asset_keys=["SUFFIX_OF_STABILITY"],
                min_misc_stats=1
            )

    def search_for_lancers_gauntlets_of_alacrity(self):
        if self.look_for_lancers_gauntlets_of_alacrity:
            self.search_for_item(
                item_description="lancers_gauntlets_of_alacrity",
                item_type_asset_keys=["GAUNTLETS"],
                item_stat_asset_keys_required=["PREFIX_LANCERS"],
                item_misc_stat_asset_keys=["SUFFIX_OF_ALACRITY"],
                min_misc_stats=1
            )

    def search_for_item(
            self,
            item_description="",
            item_type_asset_keys=[],
            item_type_asset_threshold=0.7,
            item_stat_asset_keys_required=[],
            item_stat_asset_keys_avoid=[],
            item_misc_stat_asset_keys=[],
            min_misc_stats=0,
            item_stat_asset_threshold=0.94):

        item_pos = []
        item_pos_sorted = []
        for item_key in item_type_asset_keys:
            self.mouse_over(self.mouse_reset)
            img = grab().copy()
            template_matches = TemplateFinder(True).search_multi(item_key, img, threshold=item_type_asset_threshold,
                                                                 roi=self.roi_vendor)
            # Logger.debug(f"Matched {len(template_matches)} of {item_key}")
            for template_match in template_matches:
                if template_match.valid:
                    item_pos.append(template_match.center)
        for pos in item_pos:
            x_m, y_m = convert_screen_to_monitor(pos)
            coord = Coordinate(x_m, y_m)
            item_pos_sorted.append(coord)
        item_pos_sorted.sort(key=lambda x: (x.y, x.x))
        for pos in item_pos_sorted:
            avoid_item = False
            ShopperBase.mouse_over(pos)
            wait(0.1, 0.3)
            img_stats = grab()
            self.check_stats(img_stats)
            for item_stat_asset_key_avoid in item_stat_asset_keys_avoid:
                if TemplateFinder(True).search(item_stat_asset_key_avoid, img_stats, roi=self.roi_item_stats,
                                               threshold=item_stat_asset_threshold).valid:
                    avoid_item = True
            if avoid_item:
                Logger.debug(f"Matched avoidable stat. Skipping item.")
                continue
            for item_stat_asset_key_required in item_stat_asset_keys_required:
                if TemplateFinder(True).search(item_stat_asset_key_required, img_stats, roi=self.roi_item_stats,
                                               threshold=item_stat_asset_threshold).valid:
                    Logger.debug(f"Matched {item_stat_asset_key_required}")
                    if item_misc_stat_asset_keys is None or min_misc_stats == 0:
                        self.buy_item(item_description)
                    misc_stat_count = 0
                    for item_misc_stat_asset_key in item_misc_stat_asset_keys:
                        if TemplateFinder(True).search(item_misc_stat_asset_key, img_stats, roi=self.roi_item_stats,
                                                       threshold=item_stat_asset_threshold).valid:
                            misc_stat_count += 1
                            Logger.debug(f"Matched {item_misc_stat_asset_key}. Misc stat {misc_stat_count} of {min_misc_stats}")
                            if misc_stat_count >= min_misc_stats:
                                self.buy_item(item_description)
        return

    def is_trade_open(self):
        img = grab().copy()
        trade_window = TemplateFinder(True).search("TRADE_WINDOW", img, roi=self.trade_roi)
        return trade_window.valid

ShopperBase.register(tuple)

assert issubclass(tuple, ShopperBase)
assert isinstance((), ShopperBase)
