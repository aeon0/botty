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


class LarzukShopper(ShopperBase):

    def __init__(self):
        self.look_for_warcry_weapon = Config().shop["shop_warcry_weapon"]
        self.look_for_jewelers_armor_of_the_whale = Config().shop["shop_jewelers_armor_of_the_whale"]
        self.look_for_resist_belt_of_the_whale = Config().shop["shop_resist_belt_of_the_whale"]
        self.look_for_resist_belt_of_wealth = Config().shop["shop_resist_belt_of_wealth"]
        self.look_for_artisans_helm_of_the_whale = Config().shop["shop_artisans_helm_of_the_whale"]
        self.look_for_artisans_helm_of_stability = Config().shop["shop_artisans_helm_of_stability"]
        self._pather = Pather()
        self._char: IChar = Basic(Config().basic, self._pather)
        # Create Town Manager
        a5 = A5(self._pather, self._char)
        a4 = A4(self._pather, self._char)
        a3 = A3(self._pather, self._char)
        a2 = A2(self._pather, self._char)
        a1 = A1(self._pather, self._char)
        self.harrogath = A5(self._pather, self._char)
        self._town_manager = TownManager(a1, a2, a3, a4, a5)
        self._curr_loc: Union[bool, Location] = None
        super(LarzukShopper, self).__init__()
        return

    def get_name(self):
        return "Larzuk"

    def run(self):
        Logger.info(f"Personal {self.get_name()} Shopper at your service! Hang on, running some errands...")
        self._char.discover_capabilities()
        self.get_tabs()
        self.shop_loop()

    def shop_loop(self):
        while True:
            open_npc_menu(Npc.LARZUK)
            press_npc_btn(Npc.LARZUK, "trade_repair")
            time.sleep(0.1)
            for search_tab in self.search_tabs:
                self.click_tab(search_tab)
                if search_tab == 1:
                    self.search_for_jewelers_armor_of_the_whale()
                    self.search_for_resist_belt_of_the_whale()
                    self.search_for_resist_belt_of_wealth()
                    self.search_for_artisans_helm_of_the_whale()
                    self.search_for_artisans_helm_of_stability()
                else:
                    self.search_for_warcry_weapon()

            self.reset_shop()

    def reset_shop(self):
        """
        Should be near Larzuk before and after script runs
        """
        self.move_shopper(-150, -10, 2.5)
        self._curr_loc = Location.A5_STASH
        self.harrogath.open_wp(self._curr_loc)
        wait(0.2, 0.5)
        if waypoint.use_wp("Frigid Highlands"):
            wait(0.2, 0.4)
            self.move_shopper(-100, 65, 0.3)
            self.harrogath.open_frigid_wp()
            waypoint.use_wp("Harrogath")
            wait(0.2, 0.4)
            self.move_shopper(200, 20, 2.5)

    def get_tabs(self):
        """
        Sets up which tabs we want to search in
        """
        if self.look_for_jewelers_armor_of_the_whale or self.look_for_resist_belt_of_the_whale or self.look_for_resist_belt_of_wealth or self.look_for_artisans_helm_of_the_whale or self.look_for_artisans_helm_of_stability:
            self.search_tabs.add(1)
        if self.look_for_warcry_weapon:
            self.search_tabs.add(2)
            self.search_tabs.add(3)
