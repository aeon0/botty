from bot import Bot
from logger import Logger
import keyboard
import os
from config import Config
from utils.color_checker import run_color_checker
from version import __version__
from utils.remove_key_flags import remove_key_flags, LPMSG, TranslateMessage, DispatchMessage, GetMessage
from utils.remove_mouse_flags import remove_mouse_flag
from utils.auto_settings import adjust_settings
import threading
from beautifultable import BeautifulTable
import time
import logging


def start_bot():
    try:
        bot = Bot()
        bot.start()
    except KeyboardInterrupt:
        Logger.info('Exit (ctrl+c)') or exit()

def remove_flags():
    remove_key_flags()
    remove_mouse_flag()
    msg = LPMSG()
    while not GetMessage(msg, 0, 0, 0):
        TranslateMessage(msg)
        DispatchMessage(msg)

if __name__ == "__main__":
    remove_flags_thread = threading.Thread(target=remove_flags)
    remove_flags_thread.start()
    config = Config()
    if config.general["logg_lvl"] == "info":
        Logger.init(logging.INFO)
    elif config.general["logg_lvl"] == "debug":
        Logger.init(logging.DEBUG)
    else:
        print(f"ERROR: Unkown logg_lvl {config.general['logg_lvl']}. Must be one of [info, debug]")

    # If anything seems to go wrong, press f12 and the bot will force exit
    keyboard.add_hotkey(config.general["exit_key"], lambda: Logger.info(f'Force Exit') or os._exit(1))

    print(f"============ Botty {__version__} ============")
    print("\nFor gettings started and documentation\nplease read https://github.com/aeon0/botty\n")
    table = BeautifulTable()
    table.rows.append([config.general['auto_settings_key'], "Adjust D2R settings"])
    table.rows.append([config.general['color_checker_key'], "Color test mode "])
    table.rows.append([config.general['resume_key'], "Start bot"])
    table.rows.append([config.general['exit_key'], "Stop bot"])
    table.columns.header = ["hotkey", "action"]
    print(table)
    print("\n")

    while 1:
        if keyboard.is_pressed(config.general['resume_key']):
            start_bot()
            break
        if keyboard.is_pressed(config.general['auto_settings_key']):
            adjust_settings()
        elif keyboard.is_pressed(config.general['color_checker_key']):
            run_color_checker()
            break
        time.sleep(0.02)

    remove_flags_thread.join()
    print("Press Enter to exit ...")
    input()
