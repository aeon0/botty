import datetime
import os
import time
import math
import random
from typing import Dict, Tuple, Union, List, Callable

import keyboard
import numpy as np

from screen import convert_screen_to_monitor, grab, convert_abs_to_monitor, convert_screen_to_abs, convert_monitor_to_screen
from config import Config
from logger import Logger
from npc_manager import Npc, open_npc_menu, press_npc_btn
import template_finder
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

    def __init__(self):

        # Set look_for variables to False if you dont like your personal shopper to look for these
        # Obviously something need to be set to True, or your shopper will be very confused
        self.look_for_scepters = Config().shop["shop_hammerdin_scepters"]
        self.speed_factor = 1.0 + Config().shop["speed_factor"]
        if (self.speed_factor <= 0):
            Logger.error("Can not use a speed factor less than negative 1!! Please update shop.ini. Exiting.")
            os._exit(0)
        self.apply_pather_adjustment = Config().shop["apply_pather_adjustment"]

        self.run_count = 0
        self.start_time = time.time()

        # items config
        self.roi_shop_item_stats = [0, 0, Config().ui_pos["screen_width"] // 2, Config().ui_pos["screen_height"] - 100]
        self.roi_vendor = Config().ui_roi["left_inventory"]
        self.rx, self.ry, _, _ = self.roi_vendor
        self.sb_x, self.sb_y = convert_screen_to_monitor((180, 77))
        self.c_x, self.c_y = convert_screen_to_monitor((Config().ui_pos["center_x"], Config().ui_pos["center_y"]))
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
            open_npc_menu(Npc.DROGNAN)
            press_npc_btn(Npc.DROGNAN, "trade")
            time.sleep(0.1)
            img = grab()

            if self.look_for_scepters is True:
                mouse.move(self.sb_x, self.sb_y, randomize=3, delay_factor=[0.6, 0.8])
                wait(0.05, 0.1)
                mouse.press(button="left")
                wait(0.05, 0.1)
                mouse.release(button="left")
                wait(0.3, 0.4)

                # Search for items
                item_pos = []
                img = grab().copy()
                item_keys = ["SCEPTER1", "SCEPTER2", "SCEPTER3", "SCEPTER4", "SCEPTER5"]
                template_matches = template_finder.search_all(item_keys, img, roi=self.roi_vendor)
                for template_match in template_matches:
                    item_pos.append(template_match.center_monitor)

                # check out each item
                for pos in item_pos:
                    mouse.move(*pos, randomize=3, delay_factor=[0.5, 0.6])
                    wait(0.5, 0.6)
                    img_stats = grab()

                    # First check for +2 Paladin Skills. This weeds out most scepters right away.
                    if template_finder.search("2_TO_PALADIN_SKILLS", img_stats, roi=self.roi_shop_item_stats, threshold=0.94).valid:
                        # Has 2 Pally skills, check blessed hammers next
                        if template_finder.search("TO_BLESSED_HAMMERS", img_stats, roi=self.roi_shop_item_stats, threshold=0.9).valid:
                            # Has 2 Pally skills AND Blessed Hammers, check Concentration next
                            if template_finder.search("TO_CONCENTRATION", img_stats, roi=self.roi_shop_item_stats, threshold=0.9).valid:
                                # Has 2 Pally skills AND Blessed Hammers AND Concentration. We're good! Buy it!
                                mouse.click(button="right")
                                Logger.info(f"Item bought!")
                                self.items_bought += 1
                                time.sleep(1)

                    self.items_evaluated += 1

            keyboard.send("esc")

            # Done with this shopping round
            self.reset_shop()
            self.run_count += 1

    def reset_shop(self):
        # We want to walk out the town exit to the top right and come back down to drognan
        # This can probably be tweaked but seems to work well enough for now.

        # Exit town
        pos_m = convert_abs_to_monitor((200, -100))
        mouse.move(pos_m[0], pos_m[1])
        self.hold_move(pos_m, time_held=(3.0 / self.speed_factor))

        # Return to town
        pos_m = convert_abs_to_monitor((-200, 100))
        mouse.move(pos_m[0], pos_m[1])
        self.hold_move(pos_m, time_held=(2.0 / self.speed_factor))

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
        mouse.move(x, y, randomize=5, delay_factor=[factor*0.1, factor*0.14])
        wait(0.012, 0.02)
        mouse.press(button="left")
        wait(time_held - 0.05, time_held + 0.05)
        mouse.release(button="left")
