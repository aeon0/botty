from shop.shopper_base import ShopperBase
import datetime
import os
import time
import math

import keyboard
import numpy as np

from screen import grab, convert_screen_to_monitor
from config import Config
from logger import Logger
from npc_manager import Npc, open_npc_menu, press_npc_btn
from template_finder import TemplateFinder
from utils.custom_mouse import mouse
from utils.misc import wait, load_template

from messages import Messenger


def exit(run_obj):
    run_time = str(datetime.timedelta(seconds=round(time.time() - run_obj.start_time)))
    Logger.info("Exiting shopping mall...")
    print(
        "STATS \truns \t\ttime \t\tias_gloves_seen \tgloves_bought \tclaws_evaluated \tclaws_bought\n"
        f"\t{run_obj.run_count} \t\t{run_time}"
        f"\t\t{run_obj.ias_gloves_seen} \t\t\t{run_obj.gloves_bought} \t\t{run_obj.claws_evaluated} \t\t\t{run_obj.claws_bought}"
    )
    os._exit(0)


def wait_for_loading_screen(timeout):
    start = time.time()
    while time.time() - start < timeout:
        img = grab()
        is_loading_black_roi = np.average(img[:700, 0:250]) < 4.0
        if is_loading_black_roi:
            return True
    return False


class AnyaShopper(ShopperBase):
    """
    Shop at Anya for 20 ias, +3 java skill gloves and more...

    In order to start the shopping bot:
    1.) Run this this file in Python.
    2.) Be ingame in Harrogath (act 5 town).
    3.) Stand close to Anya and the red portal.
    4.) While being ingame, press resume_key (default F11) to start the shopping, and exit_key (default F12) to stop it.
    """

    def __init__(self):
        # Set look_for variables to False if you dont like your personal shopper to look for these
        # Obviously something need to be set to True, or your shopper will be very confused
        # For the trap claw scores use:
        # 7 if you are happy with any + to traps or +2 assassin
        # 9 if you want at least +2 assassin or two useful trap stats
        # 11 if you want at least +3 traps or +2 and a sentry bonus
        # Similar for melee claws but not really worth keeping any less that 11 here since you really want both +2 assassin and a useful other stat, feedback needed
        self.look_for_plus_2_gloves = Config().shop["shop_2_skills_ias_gloves"]
        self.look_for_plus_3_gloves = Config().shop["shop_3_skills_ias_gloves"]
        self.look_for_trap_claws = Config().shop["shop_trap_claws"]
        self.trap_claw_min_score = Config().shop["trap_min_score"]
        self.look_for_melee_claws = Config().shop["shop_melee_claws"]
        self.melee_claw_min_score = Config().shop["melee_min_score"]
        self.look_for_warcry_stick = Config().shop["shop_for_warcry_stick"]
        self.look_for_jewelers_armor_of_the_whale = Config().shop["shop_jewelers_armor_of_the_whale"]
        self.look_for_resist_belt_of_the_whale = Config().shop["shop_resist_belt_of_the_whale"]
        self.look_for_resist_belt_of_wealth = Config().shop["shop_resist_belt_of_wealth"]
        self.look_for_artisans_helm_of_the_whale = Config().shop["shop_artisans_helm_of_the_whale"]
        self.look_for_artisans_helm_of_stability = Config().shop["shop_artisans_helm_of_stability"]
        self.look_for_lancers_gauntlets_of_alacrity = Config().shop["shop_lancers_gauntlets_of_alacrity"]
        self._messenger = Messenger()
        self.run_count = 0
        self.start_time = time.time()
        self.ias_gloves_seen = 0
        self.gloves_bought = 0
        # Claws config
        self.roi_claw_stats = [0, 0, Config().ui_pos["screen_width"] // 2, Config().ui_pos["screen_height"] - 100]
        self.roi_vendor = Config().ui_roi["left_inventory"]
        self.rx, self.ry, _, _ = self.roi_vendor
        self.sb_x, self.sb_y = convert_screen_to_monitor((180, 77))
        self.c_x, self.c_y = convert_screen_to_monitor((Config().ui_pos["center_x"], Config().ui_pos["center_y"]))
        self.claws_evaluated = 0
        self.claws_bought = 0
        super(AnyaShopper, self).__init__()

    def get_name(self):
        return "Anya"

    def run(self):
        Logger.info("Personal Anya Shopper at your service! Hang on, running some errands...")
        self.get_tabs()
        self.shop_loop()

    def shop_loop(self):
        asset_folder = "assets/shop/gloves/"

        while True:
            self.check_run_time()
            trade_is_open = False
            while not trade_is_open:
                open_npc_menu(Npc.ANYA)
                press_npc_btn(Npc.ANYA, "trade")
                trade_is_open = self.is_trade_open()
            time.sleep(0.1)

            for search_tab in self.search_tabs:
                self.click_tab(search_tab)
                if search_tab == 1:
                    self.search_for_jewelers_armor_of_the_whale()
                    self.search_for_resist_belt_of_the_whale()
                    self.search_for_resist_belt_of_wealth()
                    self.search_for_artisans_helm_of_the_whale()
                    self.search_for_artisans_helm_of_stability()
                    self.search_for_lancers_gauntlets_of_alacrity()
                if search_tab == 4:
                    self.search_for_warcry_stick()

            if self.look_for_trap_claws is True or self.look_for_melee_claws is True:
                mouse.move(self.sb_x, self.sb_y, randomize=3, delay_factor=[0.6, 0.8])
                wait(0.05, 0.1)
                mouse.press(button="left")
                # Search for claws
                claw_pos = []
                claw_keys = ["CLAW1", "CLAW2", "CLAW3"]
                for ck in claw_keys:
                    self.mouse_over(self.mouse_reset)
                    img = grab().copy()
                    template_matches = TemplateFinder(True).search_multi(ck, img, roi=self.roi_vendor)
                    for template_match in template_matches:
                        if template_match.valid:
                            claw_pos.append(template_match.center)
                # check out each claw
                for pos in claw_pos:
                    # cv2.circle(img, pos, 3, (0, 255, 0), 2)
                    x_m, y_m = convert_screen_to_monitor(pos)
                    mouse.move(x_m, y_m, randomize=3, delay_factor=[0.5, 0.6])
                    wait(0.1, 0.3)
                    img_stats = grab()
                    trap_score = 0
                    melee_score = 0
                    if TemplateFinder(True).search("3_TO_TRAPS", img_stats, roi=self.roi_claw_stats, threshold=0.94).valid:
                        trap_score += 12
                    elif TemplateFinder(True).search("TO_TRAPS", img_stats, roi=self.roi_claw_stats, threshold=0.9).valid:
                        trap_score += 8

                    if TemplateFinder(True).search("2_TO_ASSA", img_stats, roi=self.roi_claw_stats, threshold=0.9).valid:
                        trap_score += 10
                        melee_score += 10
                    if TemplateFinder(True).search("TO_VENOM", img_stats, roi=self.roi_claw_stats, threshold=0.9).valid:
                        melee_score += 6
                    if TemplateFinder(True).search("TO_LIGHT", img_stats, roi=self.roi_claw_stats, threshold=0.9).valid:
                        trap_score += 6
                    if TemplateFinder(True).search("TO_WB", img_stats, roi=self.roi_claw_stats, threshold=0.9).valid:
                        melee_score += 2
                        trap_score += 1
                    if TemplateFinder(True).search("TO_DS", img_stats, roi=self.roi_claw_stats, threshold=0.9).valid:
                        trap_score += 4

                    self.claws_evaluated += 1

                    if trap_score > self.trap_claw_min_score and self.look_for_trap_claws is True:
                        # pick it up
                        mouse.click(button="right")
                        self._messenger.send_message(f"Bought some terrific trap Claws (score: {trap_score})")

                        Logger.info(f"Trap Claws (score: {trap_score}) bought!")
                        self.claws_bought += 1
                        time.sleep(1)

                    if melee_score > self.melee_claw_min_score and self.look_for_melee_claws is True:
                        # pick it up
                        mouse.click(button="right")
                        self._messenger.send_message(f"Bought some mad melee Claws (score: {melee_score})")
                        Logger.info(f"Melee Claws (score: {melee_score}) bought!")
                        self.claws_bought += 1
                        time.sleep(1)

            # Done with this shopping round
            self.reset_shop()
            self.run_count += 1

    def reset_shop(self):
        while 1:
            success = self.select_by_template("A5_RED_PORTAL")
            success &= wait_for_loading_screen(2)
            if success:
                break
            else:
                mouse.move(800, 450, randomize=50, delay_factor=[0.7, 0.7])
        time.sleep(2.5)
        while 1:
            success = self.select_by_template("A5_RED_PORTAL")
            success &= wait_for_loading_screen(2)
            if success:
                break
            else:
                mouse.move(800, 450, randomize=50, delay_factor=[0.7, 0.7])

    def select_by_template(self, template_type: str) -> bool:
        template_match = TemplateFinder(True).search_and_wait(template_type, timeout=10, normalize_monitor=True)
        if template_match.valid:
            mouse.move(*template_match.center)
            wait(0.1, 0.2)
            mouse.click(button="left")
            return True
        return False

    def get_tabs(self):
        """
        Sets up which tabs we want to search in
        """
        if self.look_for_jewelers_armor_of_the_whale or self.look_for_artisans_helm_of_the_whale or self.look_for_artisans_helm_of_stability or self.look_for_lancers_gauntlets_of_alacrity:
            self.search_tabs.add(1)
        if self.look_for_warcry_stick:
            self.search_tabs.add(4)
