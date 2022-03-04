import itertools
from random import randint
from config import Config
from ui_manager import detect_screen_object, wait_for_screen_object, ScreenObjects
from .inventory_collection import InventoryCollection, inspect_area
from .stash import Stash
from .gem_picking import SimpleGemPicking
from item.item_finder import ItemFinder
from screen import convert_screen_to_monitor, grab
from utils.custom_mouse import mouse
from utils.misc import wait
from version import __version__
from logger import Logger
from game_stats import GameStats
from template_finder import TemplateFinder
import numpy as np
import keyboard
import cv2
from inventory import personal
from inventory.stash import move_to_stash_tab

FLAWLESS_GEMS = [
    "FLAWLESS_TOPAZ",
    "FLAWLESS_AMETHYST",
    "FLAWLESS_SAPPHIRE",
    "FLAWLESS_DIAMOND",
    "FLAWLESS_RUBY",
    "FLAWLESS_EMERALD",
    "FLAWLESS_SKULL"
]

PERFECT_GEMS = [
    "PERFECT_TOPAZ",
    "PERFECT_AMETHYST",
    "PERFECT_SAPPHIRE",
    "PERFECT_DIAMOND",
    "PERFECT_RUBY",
    "PERFECT_EMERALD",
    "PERFECT_SKULL"
]


class Transmute:
    @staticmethod
    def _wait():
        wait(0.2, 0.3)

    def __init__(self, game_stats: GameStats) -> None:
        self._game_stats = game_stats
        self._last_game = 0

    def pick_from_area(self, column, row, roi):
        slot_w = Config().ui_pos["slot_width"]
        slot_h = Config().ui_pos["slot_height"]
        offset_y = (row+0.5)*slot_h
        offset_x = (column+0.5)*slot_w
        x, y, _, _ = roi
        x, y = convert_screen_to_monitor(
            (x + offset_x, y + offset_y))
        mouse.move(x, y)
        self._wait()
        keyboard.send('ctrl', do_release=False)
        self._wait()
        mouse.click("left")
        self._wait()
        keyboard.release('ctrl')
        self._wait()

    def open_cube(self):
        move_to_stash_tab(0)
        match = detect_screen_object(ScreenObjects.CubeInventory)
        if match.valid:
            x, y = convert_screen_to_monitor(match.center)
            mouse.move(x, y)
            self._wait()
            mouse.click("right")
            self._wait()
        else:
            Logger.error(f"Can't find cube: {match.score}")

    def transmute(self):
        match = detect_screen_object(ScreenObjects.CubeOpened)
        if match.valid:
            x, y = convert_screen_to_monitor(match.center)
            mouse.move(x, y)
            self._wait()
            mouse.click("left")
            self._wait()

    def close_cube(self):
        self._wait()
        keyboard.send("esc")

    def stash_all_items(self):
        personal.stash_all_items(
            Config().char["num_loot_columns"], ItemFinder())

    def pick_from_cube_at(self, column, row):
        return self.pick_from_area(column, row, Config().ui_roi["cube_area_roi"])

    def pick_from_inventory_at(self, column, row):
        return self.pick_from_area(column, row, Config().ui_roi["right_inventory"])

    def pick_from_stash_at(self, index, column, row):
        move_to_stash_tab(index)
        return self.pick_from_area(column, row, Config().ui_roi["left_inventory"])

    def _is_slot_empty(self, img, treshold=16.0):
        slot_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        avg_brightness = np.average(slot_img[:, :, 2])
        return avg_brightness > treshold

    def inspect_inventory_area(self, known_items) -> InventoryCollection:
        return inspect_area(4, Config().char["num_loot_columns"], Config().ui_roi["right_inventory"], known_items)

    def inspect_stash(self) -> Stash:
        stash = Stash()
        for i in range(4):
            move_to_stash_tab(i)
            wait(0.4, 0.5)
            tab = inspect_area(
                10, 10, Config().ui_roi["left_inventory"], FLAWLESS_GEMS)
            stash.add_tab(i, tab)
        return stash

    def put_back_to_stash_randomly(self) -> None:
        flawless_gems = self.inspect_inventory_area(FLAWLESS_GEMS)
        pick = []
        for gem in flawless_gems.get_types():
            while flawless_gems.get_item_count(type=gem) > 0:
                row,_,col,_ = flawless_gems.pop_by_type(gem)
                pick.append((randint(0, 3), col, row))
        for tab, x, y in sorted(pick, key=lambda x: x[0]):
            move_to_stash_tab(tab)
            self.pick_from_inventory_at(x, y)

    def select_tab_with_enough_space(self, s: Stash) -> None:
        tabs_priority = Config()._transmute_config["stash_destination"]
        for tab in tabs_priority:
            if s.get_empty_on_tab(tab) > 0:
                move_to_stash_tab(tab)
                break

    def put_back_all_gems(self, s: Stash) -> None:
        Logger.info(
            f'Putting back gems in the following stash tabs (by priority): {Config()._transmute_config["stash_destination"]}')
        perfect_gems = self.inspect_inventory_area(
            PERFECT_GEMS + FLAWLESS_GEMS)

        for gem in perfect_gems.get_types():
            while perfect_gems.get_item_count(type=gem) > 0:
                self.select_tab_with_enough_space(s)
                row, _, col, _ = perfect_gems.pop_by_type(gem)
                self.pick_from_inventory_at(col, row)

    def should_transmute(self) -> bool:
        every_x_game = Config()._transmute_config["transmute_every_x_game"]
        if every_x_game is None or every_x_game == "" or int(every_x_game) <= 0:
            return False
        return self._game_stats._game_counter - self._last_game >= int(every_x_game)

    def run_transmutes(self, force=False) -> None:
        gold_btn = wait_for_screen_object(ScreenObjects.GoldBtnInventory, time_out = 20)
        if not gold_btn.valid:
            Logger.error("Could not determine to be in stash menu. Continue...")
            return
        if not force and not self.should_transmute():
            Logger.info(f"Skipping transmutes. Force: {force}, Game#: {self._game_stats._game_counter}")
            return None
        self._run_gem_transmutes()

    def check_cube_empty(self) -> bool:
        self.open_cube()
        area = self.inspect_cube()
        self.close_cube()
        return area.get_empty_count() == 12

    def inspect_cube(self)-> InventoryCollection:
        return inspect_area(4, 3, roi=Config().ui_roi["cube_area_roi"], known_items=FLAWLESS_GEMS)

    def _run_gem_transmutes(self) -> None:
        Logger.info("Starting gem transmute")
        self._last_game = self._game_stats._game_counter
        s = self.inspect_stash()
        algorithm = SimpleGemPicking(s)
        inv = self.inspect_inventory_area(FLAWLESS_GEMS)
        is_cube_empty = None
        while True:
            while inv.get_empty_count() >= 3:
                next_batch = algorithm.next_batch()
                is_cube_empty = self.check_cube_empty() if is_cube_empty is None else is_cube_empty
                if not is_cube_empty:
                    Logger.warning("Some items detected in the cube. Skipping transmute")
                    break
                if next_batch is None:
                    Logger.info("No more gems to cube")
                    break
                for tab, gem, y, x in next_batch:
                    self.pick_from_stash_at(tab, x, y)
                inv = self.inspect_inventory_area(FLAWLESS_GEMS)
            if inv.get_item_count() >= 3:
                self.open_cube()
                for gem in inv.get_types():
                    while inv.get_item_count(type=gem) > 0:
                        for _ in range(3):
                            row, _, col, _ = inv.pop_by_type(gem)
                            self.pick_from_inventory_at(col, row)
                        self.transmute()
                        self.pick_from_cube_at(2, 3)
                self.close_cube()
                self.put_back_all_gems(s)
            else:
                self.put_back_all_gems(s)
                break
        Logger.info("Finished gem transmute")
