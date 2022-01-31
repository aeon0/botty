from beautifultable import BeautifulTable
import logging
import traceback
import keyboard
import time
import os
from shop.anya import AnyaShopper
from shop.drognan import DrognanShopper
from config import Config
from logger import Logger
from version import __version__


def main():
    config = Config()
    if config.advanced_options["logg_lvl"] == "info":
        Logger.init(logging.INFO)
    elif config.advanced_options["logg_lvl"] == "debug":
        Logger.init(logging.DEBUG)
    else:
        print(f"ERROR: Unkown logg_lvl {config.advanced_options['logg_lvl']}. Must be one of [info, debug]")

    keyboard.add_hotkey(config.advanced_options["exit_key"], lambda: Logger.info(f'Force Exit') or os._exit(1))

    print(f"============ Shop {__version__} [name: {config.general['name']}] ============")
    table = BeautifulTable()
    table.rows.append(["f10", "Shop at Drognan (for D2R Classic)"])
    table.rows.append(["f11", "Shop at Anya"])
    table.rows.append([config.advanced_options['exit_key'], "Stop shop"])
    table.columns.header = ["hotkey", "action"]
    print(table)
    print("\n")

    while 1:
        if keyboard.is_pressed("f10"):
            merchant = DrognanShopper(config)
            merchant.run()
            break
        if keyboard.is_pressed("f11"):
            merchant = AnyaShopper(config)
            merchant.run()
            break
        time.sleep(0.02)

if __name__ == "__main__":
    # To avoid cmd just closing down, except any errors and add a input() to the end
    try:
        main()
    except:
        traceback.print_exc()
    print("Press Enter to exit ...")
    input()
