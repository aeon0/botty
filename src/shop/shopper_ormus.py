from shop.shopper_base import ShopperBase
import datetime
import os
import time
import keyboard
import numpy as np
import shop.shop_helpers
from shop.shop_helpers import Coordinate
from screen import grab, convert_screen_to_monitor, convert_screen_to_abs, convert_abs_to_monitor
from config import Config
from logger import Logger
from npc_manager import Npc, open_npc_menu, press_npc_btn
from template_finder import TemplateFinder
from utils.custom_mouse import mouse
from utils.misc import wait, load_template
from ui import waypoint
from messages import Messenger


class OrmusShopper(ShopperBase):

    def __init__(self):
        self.look_for_staff_of_teleportation = Config().shop["shop_weapon_teleport"]
        super(OrmusShopper, self).__init__()
        return

    def get_name(self):
        return "Ormus"

    def run(self):
        Logger.info(f"Personal {self.get_name()} Shopper at your service! Hang on, running some errands...")
        Logger.debug(f"look_for_staff_of_teleportation={self.look_for_staff_of_teleportation}")
        self.get_tabs()
        self.shop_loop()

    def shop_loop(self):
        while True:
            open_npc_menu(Npc.ORMUS)
            press_npc_btn(Npc.ORMUS, "trade")
            time.sleep(0.1)

            for search_tab in self.search_tabs:
                self.click_tab(search_tab)
                if self.look_for_staff_of_teleportation:
                    staff_pos = []
                    staff_pos_sorted = []
                    img = grab().copy()
                    staff_keys = ["BATTLE_STAFF", "WAR_STAFF", "GNARLED_STAFF"]
                    for staff_key in staff_keys:
                        template_matches = TemplateFinder(True).search_multi(staff_key, img, threshold=0.7, roi=self.roi_vendor)
                        # Logger.debug(f"Found {len(template_matches)} {staff_key}")
                        for template_match in template_matches:
                            if template_match.valid:
                                staff_pos.append(template_match.center)
                    for pos in staff_pos:
                        x_m, y_m = convert_screen_to_monitor(pos)
                        coord = Coordinate()
                        coord.x = x_m
                        coord.y = y_m
                        staff_pos_sorted.append(coord)
                    staff_pos_sorted.sort(key=lambda x: (x.y, x.x))
                    for pos in staff_pos_sorted:
                        ShopperBase.mouse_over(pos)
                        img_stats = grab()
                        self.check_stats(img_stats)
                        if TemplateFinder(True).search("SUFFIX_OF_TELEPORTATION", img_stats, roi=self.roi_item_stats, threshold=0.94).valid:
                            self.buy_item("staff_of_teleportation")

            self.reset_shop()

    def reset_shop(self):
        """
        Should be near Ormus before and after script runs
        """
        # We want to walk out the town exit to the top right and come back down to Ormus
        # This can probably be tweaked but seems to work well enough for now.

        Logger.debug("Resetting Shop")

        # Exit town
        # Move down into nook
        self.move_shopper(150, 100, 2.8)
        # Move out of the nook
        self.move_shopper(-150, -100, 0.8)
        # Move to the bridge
        self.move_shopper(200, -120, 9.2)
        # Come back across bridge
        self.move_shopper(-200, 120, 8.7)
        # Turn around ziggurat
        self.move_shopper(-150, -100, 0.9)

    # TODO Make this abstract
    def get_tabs(self):
        """
        Sets up which tabs we want to search in
        """
        if self.look_for_staff_of_teleportation:
            self.search_tabs.add(2)
            self.search_tabs.add(3)
