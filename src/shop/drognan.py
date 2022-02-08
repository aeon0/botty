import datetime
import os
import time
import math
import random
from typing import Dict, Tuple, Union, List, Callable

import keyboard
import numpy as np

from screen import Screen
from config import Config
from logger import Logger
from npc_manager import NpcManager, Npc
from template_finder import TemplateFinder
from utils.custom_mouse import mouse
from utils.misc import wait


def exit(run_obj):
    run_time = str(datetime.timedelta(seconds=round(time.time() - run_obj.start_time)))
    Logger.info("Exiting shopping mall...")
    print(
        "STATS \truns \t\ttime \titems_evaluated \titems_bought\n"
        f"\t{run_obj.run_count} \t\t{run_time}"
        f"\t\t{run_obj.items_evaluated} \t\t\t{run_obj.items_bought}"
    )
    os._exit(0)


class DrognanShopper:
    """
    Shop at Drognan for Items.
    Currently supported: Hammerdin scepters

    In order to start the shopping bot:
    1.) Run this this file in Python.
    2.) Be ingame in Lut Golein (Act 2 town)
    3.) Stand close to Drognan and the town exit (must be top right layout)
    4.) While being ingame, press resume_key (default F11) to start the shopping, and exit_key (default F12) to stop it.
    """

    def __init__(self, config: Config):
        self._config = config

        # Set look_for variables to False if you dont like your personal shopper to look for these
        # Obviously something need to be set to True, or your shopper will be very confused
        self.look_for_scepters = self._config.shop["shop_hammerdin_scepters"]
        self.speed_factor = 1.0 + self._config.shop["speed_factor"]
        if (self.speed_factor <= 0):
            Logger.error("Can not use a speed factor less than negative 1!! Please update shop.ini. Exiting.")
            os._exit(0)
        self.apply_pather_adjustment = self._config.shop["apply_pather_adjustment"]

        self._screen = Screen()
        self._template_finder = TemplateFinder(self._screen,  ["assets\\templates", "assets\\npc", "assets\\shop"], save_last_res=True)
        self._npc_manager = NpcManager(
            screen=self._screen, template_finder=self._template_finder
        )
        self.run_count = 0
        self.start_time = time.time()

        # items config
        self.roi_shop_item_stats = [0, 0, config.ui_pos["screen_width"] // 2, config.ui_pos["screen_height"] - 100]
        self.roi_vendor = config.ui_roi["left_inventory"]
        self.rx, self.ry, _, _ = self.roi_vendor
        self.sb_x, self.sb_y = self._screen.convert_screen_to_monitor((180, 77))
        self.c_x, self.c_y = self._screen.convert_screen_to_monitor((config.ui_pos["center_x"], config.ui_pos["center_y"]))
        self.items_evaluated = 0
        self.items_bought = 0

    def run(self):
        Logger.info("Personal Drognan Shopper at your service! Hang on, running some errands...")
        self.reset_shop()
        self.shop_loop()

    def shop_loop(self):

        # This is the main shopping loop. It can be further generalized to more easily support new items,
        # But this is sufficient for now.
        while True:
            self._npc_manager.open_npc_menu(Npc.DROGNAN)
            self._npc_manager.press_npc_btn(Npc.DROGNAN, "trade")
            time.sleep(0.1)
            img = self._screen.grab()

            if self.look_for_scepters is True:
                mouse.move(self.sb_x, self.sb_y, randomize=3, delay_factor=[0.6, 0.8])
                wait(0.05, 0.1)
                mouse.press(button="left")
                wait(0.05, 0.1)
                mouse.release(button="left")
                wait(0.3, 0.4)

                # Search for items
                item_pos = []
                img = self._screen.grab().copy()
                item_keys = ["SCEPTER1", "SCEPTER2", "SCEPTER3", "SCEPTER4", "SCEPTER5"]
                for ck in item_keys:
                    template_match = self._template_finder.search(ck, img, roi=self.roi_vendor)
                    if template_match.valid:
                        (y, x) = np.where(self._template_finder.last_res >= 0.6)
                        for (x, y) in zip(x, y):
                            new_pos = [x + self.rx + 16, y + self.ry + 50]
                            # check if pos already exists in item_pos
                            exists_already = False
                            for pos in item_pos:
                                dist = math.dist(new_pos, pos)
                                if dist < 10:
                                    exists_already = True
                            if not exists_already:
                                item_pos.append(new_pos)

                # check out each item
                for pos in item_pos:
                    x_m, y_m = self._screen.convert_screen_to_monitor(pos)
                    mouse.move(x_m, y_m, randomize=3, delay_factor=[0.5, 0.6])
                    wait(0.5, 0.6)
                    img_stats = self._screen.grab()

                    # First check for +2 Paladin Skills. This weeds out most scepters right away.
                    if self._template_finder.search("2_TO_PALADIN_SKILLS", img_stats, roi=self.roi_shop_item_stats, threshold=0.94).valid:
                        # Has 2 Pally skills, check blessed hammers next
                        if self._template_finder.search("TO_BLESSED_HAMMERS", img_stats, roi=self.roi_shop_item_stats, threshold=0.9).valid:
                            # Has 2 Pally skills AND Blessed Hammers, check Concentration next
                            if self._template_finder.search("TO_CONCENTRATION", img_stats, roi=self.roi_shop_item_stats, threshold=0.9).valid:
                                # Has 2 Pally skills AND Blessed Hammers AND Concentration. We're good! Buy it!
                                mouse.click(button="right")
                                Logger.info(f"Item bought!")
                                self.items_bought += 1
                                time.sleep(1)

                    self.items_evaluated += 1

            keyboard.send("space")

            # Done with this shopping round
            self.reset_shop()
            self.run_count += 1

    def reset_shop(self):
        # We want to walk out the town exit to the top right and come back down to drognan
        # This can probably be tweaked but seems to work well enough for now.

        # Exit town
        pos_m = self._screen.convert_abs_to_monitor((200, -100))
        mouse.move(pos_m[0], pos_m[1])
        self.hold_move(pos_m, time_held=(3.0 / self.speed_factor))

        # Return to town
        pos_m = self._screen.convert_abs_to_monitor((-200, 100))
        mouse.move(pos_m[0], pos_m[1])
        self.hold_move(pos_m, time_held=(2.0 / self.speed_factor))

    # A variation of the move() function from pather.py
    def hold_move(self, pos_monitor: Tuple[float, float], time_held: float = 2.0):
        factor = self._config.advanced_options["pathing_delay_factor"]
        # in case we want to walk we actually want to move a bit before the point cause d2r will always "overwalk"
        pos_screen = self._screen.convert_monitor_to_screen(pos_monitor)
        pos_abs = self._screen.convert_screen_to_abs(pos_screen)

        # This logic (from pather.py) sometimes negatively affects the shopper, so default is to skip this.
        if self.apply_pather_adjustment:
            dist = math.dist(pos_abs, (0, 0))
            min_wd = self._config.ui_pos["min_walk_dist"]
            max_wd = random.randint(int(self._config.ui_pos["max_walk_dist"] * 0.65), self._config.ui_pos["max_walk_dist"])
            adjust_factor = max(max_wd, min(min_wd, dist - 50)) / dist
            pos_abs = [int(pos_abs[0] * adjust_factor), int(pos_abs[1] * adjust_factor)]

        x, y = self._screen.convert_abs_to_monitor(pos_abs)
        mouse.move(x, y, randomize=5, delay_factor=[factor*0.1, factor*0.14])
        wait(0.012, 0.02)
        mouse.press(button="left")
        wait(time_held - 0.05, time_held + 0.05)
        mouse.release(button="left")
