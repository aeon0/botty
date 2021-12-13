from beautifultable import BeautifulTable
import logging
import traceback
import keyboard
import time
import os
from shop.anya import AnyaShopper
from config import Config
from logger import Logger
from version import __version__

print("HERE?")

def main():
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
    table.rows.append(["f11", "Shop at Anya"])
    table.rows.append([config.general['exit_key'], "Stop shop"])
    table.columns.header = ["hotkey", "action"]
    print(table)
    print("\n")
    
    anya = AnyaShopper(config)

    while 1:
        if keyboard.is_pressed("f11"):
            anya.run()
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
