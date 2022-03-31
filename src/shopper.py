from beautifultable import BeautifulTable
import logging
import traceback
import keyboard
import time
import os
import glob
from shop.shopper_base import ShopperBase
from importlib import util
from typing import List
from config import Config
from logger import Logger
from version import __version__
from screen import start_detecting_window, stop_detecting_window


def main():
    if Config().advanced_options["logg_lvl"] == "info":
        Logger.init(logging.INFO)
    elif Config().advanced_options["logg_lvl"] == "debug":
        Logger.init(logging.DEBUG)
    else:
        print(f"ERROR: Unkown logg_lvl {Config().advanced_options['logg_lvl']}. Must be one of [info, debug]")

    keyboard.add_hotkey(Config().advanced_options["exit_key"], lambda: Logger.info(f'Force Exit') or os._exit(1))

    shoppers = load_shoppers()

    if len(shoppers) > 11:
        Logger.error(f"Too many shoppers for F key assignments: {len(shoppers)}")
        exit()

    print(f"============ Shop {__version__} [name: {Config().general['name']}] ============")
    table = BeautifulTable()
    for idx, shopper in enumerate(shoppers):
        table.rows.append([f"f{idx+1}", shopper.get_name()])
    table.rows.append([Config().advanced_options['exit_key'], "Stop shop"])
    table.columns.header = ["hotkey", "action"]
    print(table)
    print("\n")

    while 1:
        keyread = keyboard.read_key()
        if not keyread == "f12" and keyread.find("f") > -1:
            fkey_num = int(keyread.replace("f", "")) - 1
            Logger.info(f"Shopper selected: {shoppers[fkey_num].get_name()}")
            shoppers[fkey_num].run()
        time.sleep(0.2)


def load_shoppers() -> List[ShopperBase]:
    shoppers = []

    modules = glob.glob('./src/shop/shopper_*.py')
    for module in modules:
        if not module.__contains__("shopper_base"):
            head, tail = os.path.split(module)
            file_name = tail.split('.')[0]
            spec = util.spec_from_file_location(file_name, module)
            foo = util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            class_name = file_name.replace("shopper_", "")
            class_name = class_name.capitalize() + "Shopper"
            class_ = getattr(foo, class_name)
            instance = class_()
            shoppers.append(instance)
    Logger.info(f"Loaded Shoppers: {[cls.__name__ for cls in ShopperBase.__subclasses__()]}")
    return shoppers


if __name__ == "__main__":
    # To avoid cmd just closing down, except any errors and add a input() to the end
    try:
        start_detecting_window()
        time.sleep(2)
        main()
    except:
        traceback.print_exc()
    print("Press Enter to exit ...")
    input()
    stop_detecting_window()
