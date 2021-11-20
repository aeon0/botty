from bot import Bot
from game_recovery import GameRecovery
from logger import Logger
import keyboard
import os
from config import Config
from utils.color_checker import run_color_checker
from version import __version__
from utils.auto_settings import adjust_settings
from utils.misc import kill_thread, send_discord, close_down_d2
import threading
from beautifultable import BeautifulTable
import time
import logging


def run_bot(config: Config):
    game_recovery = GameRecovery()
    bot = Bot()
    bot_thread = threading.Thread(target=bot.start)
    bot_thread.start()
    do_restart = False
    keyboard.add_hotkey(config.general["exit_key"], lambda: Logger.info(f'Force Exit') or os._exit(1))
    keyboard.add_hotkey(config.general['resume_key'], lambda: bot.toggle_pause())
    while 1:
        if bot.current_game_length() > config.general["max_game_length_s"]:
            Logger.info(f"Max game length reached. Attempting to restart {config.general['name']}!")
            bot.stop()
            kill_thread(bot_thread)
            if game_recovery.go_to_hero_selection():
                do_restart = False
            break
        time.sleep(0.04)
    bot_thread.join()
    if do_restart:
        run_bot(config)
    else:
        Logger.error(f"{config.general['name']} could not recover from a max game length violation. Shutting down everything.")
        if config.general["custom_discord_hook"]:
            send_discord(f"{config.general['name']} got stuck and can not resume", config.general["custom_discord_hook"])
        close_down_d2()


if __name__ == "__main__":
    config = Config(print_warnings=True)
    if config.general["logg_lvl"] == "info":
        Logger.init(logging.INFO)
    elif config.general["logg_lvl"] == "debug":
        Logger.init(logging.DEBUG)
    else:
        print(f"ERROR: Unkown logg_lvl {config.general['logg_lvl']}. Must be one of [info, debug]")

    # create folder if they dont exist yet
    if not os.path.exists("info_screenshots"):
        os.system("mkdir info_screenshots")
    if not os.path.exists("loot_screenshots"):
        os.system("mkdir loot_screenshots")

    # If anything seems to go wrong, press f12 and the bot will force exit
    keyboard.add_hotkey(config.general["exit_key"], lambda: Logger.info(f'Force Exit') or os._exit(1))

    print(f"============ Botty {__version__} [name: {config.general['name']}] ============")
    print("\nFor gettings started and documentation\nplease read https://github.com/aeon0/botty\n")
    table = BeautifulTable()
    table.rows.append([config.general['auto_settings_key'], "Adjust D2R settings"])
    table.rows.append([config.general['color_checker_key'], "Color test mode "])
    table.rows.append([config.general['resume_key'], "Start / Pause Botty"])
    table.rows.append([config.general['exit_key'], "Stop bot"])
    table.columns.header = ["hotkey", "action"]
    print(table)
    print("\n")

    while 1:
        if keyboard.is_pressed(config.general['resume_key']):
            run_bot(config)
            break
        if keyboard.is_pressed(config.general['auto_settings_key']):
            adjust_settings()
        elif keyboard.is_pressed(config.general['color_checker_key']):
            run_color_checker()
            break
        time.sleep(0.02)

    print("Press Enter to exit ...")
    input()
