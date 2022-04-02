import time
from config import Config
from typing import Union
from logger import Logger
from shop.shopper_base import ShopperBase
from pather import Pather, Location
from town import TownManager, A1, A2, A3, A4, A5, town_manager
from char import IChar
from char.basic import Basic
from npc_manager import Npc, open_npc_menu, press_npc_btn
from ui import waypoint
from utils.misc import wait
from utils.custom_mouse import mouse


class AkaraShopper(ShopperBase):
    """
    Shop at Akara for leaf runeword bases and life tap and lower resist wands

    In order to start the shopping bot:
    1. Run this file in Python.
    2. Be in game in Rogue Encampment (act 1 town) with waypoint nearest to Akara (South). Will not work if waypoint is northerly most waypoint.
    3. Stand close to Akara.
    4. While being in game, the hotkey corresponding to Akara
    """

    def __init__(self):
        self.look_for_leaf_runeword_base = Config().shop["shop_leaf_runeword_base"]
        self.look_for_wand_of_life_tap = Config().shop["shop_weapon_life_tap"]
        self.look_for_wand_of_lower_resist = Config().shop["shop_weapon_lower_resist"]
        self._pather = Pather()
        self._char: IChar = Basic(Config().basic, self._pather)
        # Create Town Manager
        a5 = A5(self._pather, self._char)
        a4 = A4(self._pather, self._char)
        a3 = A3(self._pather, self._char)
        a2 = A2(self._pather, self._char)
        a1 = A1(self._pather, self._char)
        self.camp = A1(self._pather, self._char)
        self._town_manager = TownManager(a1, a2, a3, a4, a5)
        self._curr_loc: Union[bool, Location] = None
        super(AkaraShopper, self).__init__()
        return

    def get_name(self):
        return "Akara"

    def run(self):
        Logger.info(f"Personal {self.get_name()} Shopper at your service! Hang on, running some errands...")
        Logger.debug(f"look_for_leaf_runeword_base={self.look_for_leaf_runeword_base}")
        Logger.debug(f"look_for_wand_of_life_tap={self.look_for_wand_of_life_tap}")
        Logger.debug(f"look_for_wand_of_lower_resist={self.look_for_wand_of_lower_resist}")
        Logger.debug(f"Location: {self._curr_loc}")
        self._char.discover_capabilities()
        self.get_tabs()
        self.shop_loop()

    def shop_loop(self):
        while True:
            open_npc_menu(Npc.AKARA)
            press_npc_btn(Npc.AKARA, "trade")
            time.sleep(0.1)
            for search_tab in self.search_tabs:
                self.click_tab(search_tab)
                self.search_for_leaf_runeword_base()
                self.search_for_wand_of_life_tap()
                self.search_for_wand_of_lower_resist()

            self.reset_shop()

    def reset_shop(self):
        """
        Should be near Akara before and after script runs
        """
        self.move_shopper(-150, 100, 0.1)
        self.move_shopper(-200, -120, 2.4)
        self._curr_loc = Location.A1_WP_SOUTH
        self.camp.open_wp(self._curr_loc)
        wait(0.1, 0.4)
        if waypoint.use_wp("Cold Plains"):
            wait(0.2, 0.4)
            self.camp.open_wp(Location.A1_WP_SOUTH)
            waypoint.use_wp("Rouge Encampment")
            wait(0.2, 0.4)
            self.move_shopper(-150, 100, 0.1)
            self.move_shopper(200, 120, 3.0)
            self.move_shopper(15, 10, 0.2)


    def get_tabs(self):
        """
        Sets up which tabs we want to search in
        """
        if self.look_for_wand_of_life_tap or self.look_for_wand_of_lower_resist:
            self.search_tabs.add(2)
        if self.look_for_leaf_runeword_base:
            self.search_tabs.add(2)
            self.search_tabs.add(3)
