"""Main program to automate shopping items from merchants."""
import logging
import os
import time
import traceback

import keyboard
from beautifultable import BeautifulTable

from config import Config
from logger import Logger
from shop.anya import AnyaShopper
from shop.drognan import DrognanShopper
from version import __version__
from screen import start_detecting_window
from screen import stop_detecting_window


def main():
    """Main shopper loop."""
    if Config().advanced_options["logg_lvl"] == "info":
        Logger.init(logging.INFO)
    elif Config().advanced_options["logg_lvl"] == "debug":
        Logger.init(logging.DEBUG)
    else:
        print(f"ERROR: Unkown logg_lvl {Config().advanced_options['logg_lvl']}. Must be one of [info, debug]")

    keyboard.add_hotkey(Config().advanced_options["exit_key"], lambda: Logger.info('Force Exit') or os._exit(1))

    print(f"============ Shop {__version__} [name: {Config().general['name']}] ============")
    table = BeautifulTable()
    table.rows.append(["f10", "Shop at Drognan (for D2R Classic)"])
    table.rows.append(["f11", "Shop at Anya"])
    table.rows.append([Config().advanced_options['exit_key'], "Stop shop"])
    table.columns.header = ["hotkey", "action"]
    print(table)
    print("\n")

    merchant = None
    while not merchant:
        if keyboard.is_pressed("f10"):
            merchant = DrognanShopper()
        elif keyboard.is_pressed("f11"):
            merchant = AnyaShopper()
    keyboard.unhook_all_hotkeys()
    keyboard.add_hotkey(Config().advanced_options["exit_key"], merchant.exit)
    merchant.run()


if __name__ == "__main__":
    # To avoid cmd just closing down, except any errors and add an input() call at the end.
    try:
        start_detecting_window()
        time.sleep(2)
        main()
    except:  # pylint: disable=bare-except
        traceback.print_exc()
    print("Press Enter to exit ...")
    input()
    stop_detecting_window()
