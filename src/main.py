import threading

import keyboard
import os
from beautifultable import BeautifulTable
import logging
import traceback

from game_controller import GameController
from version import __version__
from utils.graphic_debugger import run_graphic_debugger
from utils.auto_settings import adjust_settings, backup_settings, restore_settings_from_backup

from config import Config
from logger import Logger


def start_bot(config: Config):
    game_controller = GameController()
    game_controller_thread = threading.Thread(target=game_controller.run_bot, args=[config])
    game_controller_thread.daemon = True
    game_controller_thread.start()


def main():
    config = Config(print_warnings=True)
    if config.general["logg_lvl"] == "info":
        Logger.init(logging.INFO)
    elif config.general["logg_lvl"] == "debug":
        Logger.init(logging.DEBUG)
    else:
        print(f"ERROR: Unkown logg_lvl {config.general['logg_lvl']}. Must be one of [info, debug]")

    # Create folder for debug screenshots if they dont exist yet
    os.system("mkdir stats")
    if not os.path.exists("info_screenshots") and config.general["info_screenshots"]:
        os.system("mkdir info_screenshots")
    if not os.path.exists("loot_screenshots") and config.general["loot_screenshots"]:
        os.system("mkdir loot_screenshots")

    print(f"============ Botty {__version__} [name: {config.general['name']}] ============")
    print("\nFor gettings started and documentation\nplease read https://github.com/aeon0/botty\n")
    table = BeautifulTable()
    table.rows.append([config.general['restore_settings_from_backup_key'], "Restore D2R settings from backup"])
    table.rows.append([config.general['settings_backup_key'], "Backup D2R current settings"])
    table.rows.append([config.general['auto_settings_key'], "Adjust D2R settings"])
    table.rows.append([config.general['graphic_debugger_key'], "Graphic debugger"])
    table.rows.append([config.general['resume_key'], "Start / Pause Botty"])
    table.rows.append([config.general['exit_key'], "Stop bot"])
    table.columns.header = ["hotkey", "action"]
    print(table)
    print("\n")

    keyboard.add_hotkey(config.general['auto_settings_key'], lambda: adjust_settings(config))
    keyboard.add_hotkey(config.general['graphic_debugger_key'], lambda: run_graphic_debugger())
    keyboard.add_hotkey(config.general['restore_settings_from_backup_key'], lambda: restore_settings_from_backup(config))
    keyboard.add_hotkey(config.general['settings_backup_key'], lambda: backup_settings(config))
    keyboard.add_hotkey(config.general['resume_key'], lambda c: start_bot(c), args=[config])
    keyboard.add_hotkey(config.general["exit_key"], lambda: Logger.info(f'Force Exit') or os._exit(1))
    keyboard.wait()
    print('stopped waiting')


if __name__ == "__main__":
    # To avoid cmd just closing down, except any errors and add a input() to the end
    try:
        main()
    except:
        traceback.print_exc()
    print("Press Enter to exit ...")
    input()
