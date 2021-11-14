import logging
import os
import time

import keyboard
import mouse
import screen

from config import Config
from logger import Logger
from npc_manager import NpcManager, Npc
from template_finder import TemplateFinder, load_template


def exit():
    Logger.info("Exiting...")
    os._exit(0)


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

        # Are we at the right start place?
        t1 = time.time()
        while True:
            success, pos = self._template_finder.search_and_wait("A5_RED_PORTAL", time_out=5)
            if success:
                mouse.move(*pos, duration=0.1)
                mouse.click()
                break

            if time.time() > t1 + 30:
                Logger.info("Cannot find start place :(")
                exit()
            time.sleep(3)

        self.shop_loop()

    def shop_loop(self):
        while True:
            time.sleep(3.6)
            success, pos = self._template_finder.search_and_wait("A5_RED_PORTAL")
            mouse.move(*pos, duration=0.1)
            mouse.click()
            time.sleep(1)
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
            )
            if ias_glove_found:
                mouse.move(*pos, duration=0.1)
                time.sleep(0.1)
                img = self._screen.grab()
                gg_gloves_found, pos = self._template_finder.search(
                    ref=load_template(
                        "assets/templates/javashopper/gg_gloves.png", 1.0
                    ),
                    inp_img=img,
                    threshold=0.80,
                )
                if gg_gloves_found:
                    mouse.right_click()
                    Logger.info("GG gloves bought!")
                    time.sleep(1)

            # Reset shop by using red portal
            success, pos = self._template_finder.search_and_wait("A5_RED_PORTAL")
            mouse.move(*pos, absolute=True, duration=0.1)
            mouse.click()


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
