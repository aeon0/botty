import itertools
from random import randint
from config import Config
from ui_manager import detect_screen_object, select_screen_object_match, wait_until_visible, ScreenObjects
from .inventory_collection import InventoryCollection
from .stash import Stash
from .gem_picking import SimpleGemPicking
from screen import convert_screen_to_monitor, grab
from utils.custom_mouse import mouse
from utils.misc import wait
from version import __version__
from logger import Logger
from game_stats import GameStats
import template_finder
import numpy as np
import keyboard
import cv2
from inventory import personal, common

FLAWLESS_GEMS = [
    "INVENTORY_TOPAZ_FLAWLESS",
    "INVENTORY_AMETHYST_FLAWLESS",
    "INVENTORY_SAPPHIRE_FLAWLESS",
    "INVENTORY_DIAMOND_FLAWLESS",
    "INVENTORY_RUBY_FLAWLESS",
    "INVENTORY_EMERALD_FLAWLESS",
    "INVENTORY_SKULL_FLAWLESS"
]

PERFECT_GEMS = [
    "INVENTORY_TOPAZ_PERFECT",
    "INVENTORY_AMETHYST_PERFECT",
    "INVENTORY_SAPPHIRE_PERFECT",
    "INVENTORY_DIAMOND_PERFECT",
    "INVENTORY_RUBY_PERFECT",
    "INVENTORY_EMERALD_PERFECT",
    "INVENTORY_SKULL_PERFECT"
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
        common.select_tab(0)
        if (match := detect_screen_object(ScreenObjects.CubeInventory)).valid:
            mouse.move(*match.center_monitor)
            self._wait()
            mouse.click("right")
            self._wait()
        else:
            Logger.error(f"Can't find cube: {match.score}")

    def transmute(self):
        if (match := detect_screen_object(ScreenObjects.CubeOpened)).valid:
            select_screen_object_match(match)

    def close_cube(self):
        self._wait()
        keyboard.send("esc")

    def stash_all_items(self):
        personal.stash_all_items()

    def pick_from_cube_at(self, column, row):
        return self.pick_from_area(column, row, Config().ui_roi["cube_area_roi"])

    def pick_from_inventory_at(self, column, row):
        return self.pick_from_area(column, row, Config().ui_roi["right_inventory"])

    def pick_from_stash_at(self, index, column, row):
        common.select_tab(index)
        return self.pick_from_area(column, row, Config().ui_roi["left_inventory"])

    def inspect_area(self, total_rows, total_columns, roi, known_items) -> InventoryCollection:
        result = InventoryCollection()
        x, y, w, h = roi
        img = grab()[y:y+h, x:x+w]
        slot_w = Config().ui_pos["slot_width"]
        slot_h = Config().ui_pos["slot_height"]
        for column, row in itertools.product(range(total_columns), range(total_rows)):
            y_start, y_end = row*slot_h, slot_h*(row+1)
            x_start, x_end = column*slot_w, slot_w*(column+1)
            slot_img = img[y_start:y_end, x_start:x_end]
            if not self._is_slot_empty(slot_img[+4:-4, +4:-4], treshold=36):
                result.set_empty((column, row))
            match = template_finder.search(
                known_items, slot_img, threshold=0.91, best_match=True)

            if match.valid:
                result.append(match.name, (column, row))

        return result

    def _is_slot_empty(self, img, treshold=16.0):
        slot_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        avg_brightness = np.average(slot_img[:, :, 2])
        return avg_brightness > treshold

    def inspect_inventory_area(self, known_items) -> InventoryCollection:
        return self.inspect_area(4, Config().char["num_loot_columns"], Config().ui_roi["right_inventory"], known_items)

    def inspect_stash(self) -> Stash:
        stash = Stash()
        for i in range(4):
            common.select_tab(i)
            wait(0.4, 0.5)
            tab = self.inspect_area(
                10, 10, Config().ui_roi["left_inventory"], FLAWLESS_GEMS)
            stash.add_tab(i, tab)
        return stash

    def put_back_to_stash_randomly(self) -> None:
        flawless_gems = self.inspect_inventory_area(FLAWLESS_GEMS)
        pick = []
        for gem in flawless_gems.all_items():
            while flawless_gems.count_by(gem) > 0:
                pick.append((randint(0, 3), *flawless_gems.pop(gem)))
        for tab, x, y in sorted(pick, key=lambda x: x[0]):
            common.select_tab(tab)
            self.pick_from_inventory_at(x, y)

    def select_tab_with_enough_space(self, s: Stash) -> None:
        tabs_priority = Config().configs["transmute"]["parser"]["stash_destination"]
        Config().configs["transmute"]["parser"]["stash_destination"]
        for tab in tabs_priority:
            if s.get_empty_on_tab(tab) > 0:
                common.select_tab(tab)
                break

    def put_back_all_gems(self, s: Stash) -> None:
        Logger.info(
            f'Putting back gems in the following stash tabs (by priority): {Config().configs["transmute"]["parser"]["stash_destination"]}')
        perfect_gems = self.inspect_inventory_area(
            PERFECT_GEMS + FLAWLESS_GEMS)

        for gem in perfect_gems.all_items():
            while perfect_gems.count_by(gem) > 0:
                self.select_tab_with_enough_space(s)
                self.pick_from_inventory_at(*perfect_gems.pop(gem))

    def should_transmute(self) -> bool:
        every_x_game = Config().configs["transmute"]["parser"]["transmute_every_x_game"]
        
        if every_x_game is None or every_x_game == "" or int(every_x_game) <= 0:
            return False
        return self._game_stats._game_counter - self._last_game >= int(every_x_game)

    def run_transmutes(self, force=False) -> None:
        if not wait_until_visible(ScreenObjects.GoldBtnStash, timeout = 8).valid:
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
        return area.count_empty() == 12

    def inspect_cube(self)-> InventoryCollection:
        return self.inspect_area(4, 3, roi=Config().ui_roi["cube_area_roi"], known_items=FLAWLESS_GEMS)

    def _run_gem_transmutes(self) -> None:
        Logger.info("Starting gem transmute")
        self._last_game = self._game_stats._game_counter
        s = self.inspect_stash()
        algorithm = SimpleGemPicking(s)
        inv = self.inspect_inventory_area(FLAWLESS_GEMS)
        is_cube_empty = None
        while True:
            while inv.count_empty() >= 3:
                next_batch = algorithm.next_batch()
                is_cube_empty = self.check_cube_empty() if is_cube_empty is None else is_cube_empty
                if not is_cube_empty:
                    Logger.warning("Some items detected in the cube. Skipping transmute")
                    break
                if next_batch is None:
                    Logger.info("No more gems to cube")
                    break
                for tab, gem, x, y in next_batch:
                    self.pick_from_stash_at(tab, x, y)
                inv = self.inspect_inventory_area(FLAWLESS_GEMS)
            if inv.count() >= 3:
                self.open_cube()
                for gem in inv.all_items():
                    while inv.count_by(gem) > 0:
                        for _ in range(3):
                            next = inv.pop(gem)
                            self.pick_from_inventory_at(*next)
                        self.transmute()
                        self.pick_from_cube_at(2, 3)
                self.close_cube()
                self.put_back_all_gems(s)
            else:
                self.put_back_all_gems(s)
                break
        Logger.info("Finished gem transmute")
