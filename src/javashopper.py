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



def exit():
    Logger.info("Exiting...")
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
    Shop javazon 20 ias 3 java skill gloves
    """

    def __init__(self, config):
        self._screen = screen.Screen()
        self.config = config
        self._template_finder = TemplateFinder(self._screen)
        self._npc_manager = NpcManager(
            screen=self._screen, template_finder=self._template_finder
        )

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
                ref=load_template("assets/templates/javashopper/ias_gloves.png", 1.0),
                inp_img=img,
                threshold=0.98,
                roi=self.config.ui_roi["vendor_stash"],
                normalize_monitor=True,
            )
            if ias_glove_found:
                mouse.move(*pos)
                time.sleep(0.1)
                img = self._screen.grab()
                gg_gloves_found, pos = self._template_finder.search(
                    ref=load_template(
                        "assets/templates/javashopper/gg_gloves.png", 1.0
                    ),
                    inp_img=img,
                    threshold=0.80,
                    normalize_monitor=True,
                )
                if gg_gloves_found:
                    mouse.click(button="right")
                    Logger.info("GG gloves bought!")
                    time.sleep(1)

            self.reset_shop()

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

    keyboard.add_hotkey(config.general["exit_key"], exit)

    javashopper = JavaShopper(config)
    while True:
        if keyboard.is_pressed(config.general["resume_key"]):
            javashopper.run()
            break

        time.sleep(0.05)
