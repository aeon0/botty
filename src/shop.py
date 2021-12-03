from beautifultable import BeautifulTable
import logging
import time
import keyboard
import os
from shop import anya
from config import Config
from logger import Logger
from version import __version__


if __name__ == "__main__":
    config = Config(print_warnings=True)
    if config.general["logg_lvl"] == "info":
        Logger.init(logging.INFO)
    elif config.general["logg_lvl"] == "debug":
        Logger.init(logging.DEBUG)
    else:
        print(f"ERROR: Unkown logg_lvl {config.general['logg_lvl']}. Must be one of [info, debug]")

    keyboard.add_hotkey(config.general["exit_key"], lambda: Logger.info(f'Force Exit') or os._exit(1))

    print(f"============ Shop {__version__} [name: {config.general['name']}] ============")
    table = BeautifulTable()
    table.rows.append(["f9", "Shop at Anya"])
    table.rows.append([config.general['exit_key'], "Stop shop"])
    table.columns.header = ["hotkey", "action"]
    print(table)
    print("\n")
    
    while 1:
        if keyboard.is_pressed("f9"):
            anya.main()
            break
        time.sleep(0.02)
