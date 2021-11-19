import datetime
import logging
import os
import time

from screen import Screen

import keyboard
import numpy as np
import screen

from config import Config
from logger import Logger
from npc_manager import NpcManager, Npc
from template_finder import TemplateFinder, load_template
from utils.custom_mouse import mouse
from utils.misc import wait



def exit(run_obj):
    run_time = str(datetime.timedelta(seconds=round(time.time() - run_obj.start_time)))
    Logger.info("Exiting...")
    print(
        "STATS \truns \t\ttime \t\tias_gloves_seen \tgloves_bought\n"
        f"\t{run_obj.run_count} \t\t{run_time}"
        f"\t\t{run_obj.ias_gloves_seen} \t\t\t{run_obj.gloves_bought}"
    )
    os._exit(0)


def wait_for_loading_screen(screen: Screen, time_out):
    start = time.time()
    while time.time() - start < time_out:
        img = screen.grab()
        is_loading_black_roi = np.average(img[:700, 0:250]) < 4.0
        if is_loading_black_roi:
            return True
    return False

class JavaShopper:
    """
    Shop javazon 20 ias 3 java skill gloves.

    In order to start the shopping bot:
    1.) Run this this file in Python.
    2.) Be ingame in Harrogath (act 5 town).
    3.) Stand close to Anya and the red portal.
    4.) While being ingame, press F11 (default) to start the shopping and F12 (default) to stop it.
    """

    def __init__(self, config):
        self._screen = screen.Screen()
        self.config = config
        self._template_finder = TemplateFinder(self._screen)
        self._npc_manager = NpcManager(
            screen=self._screen, template_finder=self._template_finder
        )
        self.run_count = 0
        self.start_time = time.time()
        self.ias_gloves_seen = 0
        self.gloves_bought = 0

    def run(self):
        Logger.info("STARTING JAVAZON GG GLOVES SHOPPER!")
        self.reset_shop()
        self.shop_loop()

    def shop_loop(self):
        while True:
            self._npc_manager.open_npc_menu(Npc.ANYA)
            self._npc_manager.press_npc_btn(Npc.ANYA, "trade")
            time.sleep(0.1)
            img = self._screen.grab()

            # 20 IAS gloves have a unique color so we can skip all others
            ias_glove_found, pos = self._template_finder.search(
                ref=load_template("assets/shop/gloves/ias_gloves.png", 1.0),
                inp_img=img,
                threshold=0.98,
                roi=self.config.ui_roi["vendor_stash"],
                normalize_monitor=True,
            )
            if ias_glove_found:
                self.ias_gloves_seen += 1
                mouse.move(*pos)
                time.sleep(0.1)
                img = self._screen.grab()
                gg_gloves_found, pos = self._template_finder.search(
                    ref=load_template(
                        "assets/shop/gloves/gg_gloves.png", 1.0
                    ),
                    inp_img=img,
                    threshold=0.80,
                    normalize_monitor=True,
                )
                if gg_gloves_found:
                    mouse.click(button="right")
                    Logger.info("GG gloves bought!")
                    self.gloves_bought += 1
                    time.sleep(1)

            self.reset_shop()
            self.run_count += 1

    def reset_shop(self):
        while 1:
            success = self.select_by_template("A5_RED_PORTAL")
            success &= wait_for_loading_screen(self._screen, 2)
            if success:
                break
            else:
                mouse.move(800, 450, randomize=50, delay_factor=[0.7, 0.7])
        time.sleep(3)
        while 1:
            success = self.select_by_template("A5_RED_PORTAL")
            success &= wait_for_loading_screen(self._screen, 2)
            if success:
                break
            else:
                mouse.move(800, 450, randomize=50, delay_factor=[0.7, 0.7])

    def select_by_template(self, template_type: str) -> bool:
        Logger.debug(f"Select {template_type}")
        success, screen_loc = self._template_finder.search_and_wait(template_type, time_out=10)
        if success:
            x_m, y_m = self._screen.convert_screen_to_monitor(screen_loc)
            mouse.move(x_m, y_m)
            wait(0.1, 0.2)
            mouse.click(button="left")
            return True
        return False


if __name__ == "__main__":
    config = Config()
    if config.general["logg_lvl"] == "info":
        Logger.init(logging.INFO)
    elif config.general["logg_lvl"] == "debug":
        Logger.init(logging.DEBUG)
    else:
        print(
            f"ERROR: Unkown logg_lvl {config.general['logg_lvl']}. Must be one of [info, debug]"
        )

    javashopper = JavaShopper(config)
    keyboard.add_hotkey(config.general["exit_key"], lambda: exit(run_obj=javashopper))
    while True:
        if keyboard.is_pressed(config.general["resume_key"]):
            try:
                javashopper.run()
            except Exception as e:
                Logger.logger.exception(e)
                exit(javashopper)
            break

        time.sleep(0.05)
