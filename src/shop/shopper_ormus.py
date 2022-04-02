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
        self.look_for_wand_of_life_tap = Config().shop["shop_weapon_life_tap"]
        self.look_for_wand_of_lower_resist = Config().shop["shop_weapon_lower_resist"]
        super(OrmusShopper, self).__init__()
        return

    def get_name(self):
        return "Ormus"

    def run(self):
        Logger.info(f"Personal {self.get_name()} Shopper at your service! Hang on, running some errands...")
        Logger.debug(f"look_for_staff_of_teleportation={self.look_for_staff_of_teleportation}")
        Logger.debug(f"look_for_wand_of_life_tap={self.look_for_wand_of_life_tap}")
        Logger.debug(f"look_for_wand_of_lower_resist={self.look_for_wand_of_lower_resist}")
        self.get_tabs()
        self.shop_loop()

    def shop_loop(self):
        while True:
            open_npc_menu(Npc.ORMUS)
            press_npc_btn(Npc.ORMUS, "trade")
            time.sleep(0.1)
            for search_tab in self.search_tabs:
                self.click_tab(search_tab)
                self.search_for_staff_of_teleportation()
                self.search_for_wand_of_life_tap()
                self.search_for_wand_of_lower_resist()

            self.reset_shop()

    def reset_shop(self):
        """
        Should be near Ormus before and after script runs
        """
        # We want to walk out the town exit to the top right and come back down to Ormus
        # This can probably be tweaked but seems to work well enough for now.

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
        if self.look_for_wand_of_life_tap or self.look_for_wand_of_lower_resist:
            self.search_tabs.add(2)
