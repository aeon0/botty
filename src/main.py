from dataclasses import dataclass
import keyboard
import os
from beautifultable import BeautifulTable
import logging
import traceback
import screen
import string
from version import __version__
from config import Config
from logger import Logger
from game_controller import GameController
from utils.graphic_debugger import GraphicDebuggerController
from utils.misc import restore_d2r_window_visibility
from utils.auto_settings import adjust_settings, backup_settings, restore_settings_from_backup

@dataclass
class Controllers():
    game: GameController
    debugger: GraphicDebuggerController


def start_or_pause_bot(controllers: Controllers):
    if controllers.game.is_running:
        controllers.game.toggle_pause_bot()
        screen.stop_detecting_window()
    else:
        # Kill any other controllers and start botty
        controllers.debugger.stop()
        screen.start_detecting_window()
        controllers.game.start()

def start_or_stop_graphic_debugger(controllers: Controllers):
    if controllers.debugger.is_running:
        controllers.debugger.stop()
        screen.stop_detecting_window()
    else:
        # Kill any other controller and start debugger
        screen.start_detecting_window()
        controllers.game.stop()
        controllers.debugger.start()

def on_exit():
    Logger.info(f'Force Exit')
    screen.stop_detecting_window()
    restore_d2r_window_visibility()
    os._exit(1)

def startup_checks():
    # check if paths contain non-ascii characters
    check_for_non_ascii = {
        "D2R path": Config().general["d2r_path"],
        "Windows username": os.getlogin(),
        "Botty path": os.getcwd()
    }
    for key, value in check_for_non_ascii.items():
        strip_punctuation = value.translate(str.maketrans('', '', string.punctuation))
        if not len(strip_punctuation) == len(strip_punctuation.encode()):
            print(f"\n!! WARNING: {key} ({value}) contains incompatible characters. This could result in Botty encoding errors.\n")


def main():
    # Create folder for debug screenshots if they dont exist yet
    for dir_name in ["log", "log/stats", "log/screenshots", "log/screenshots/info", "log/screenshots/items", "log/screenshots/pickit", "log/screenshots/generated"]:
        os.makedirs(dir_name, exist_ok=True)

    controllers = Controllers(
        GameController(),
        GraphicDebuggerController()
    )
    if Config().advanced_options["logg_lvl"] == "info":
        Logger.init(logging.INFO)
    elif Config().advanced_options["logg_lvl"] == "debug":
        Logger.init(logging.DEBUG)
    else:
        print(f"ERROR: Unkown logg_lvl {Config().advanced_options['logg_lvl']}. Must be one of [info, debug]")
    startup_checks()

    print(f"============ Botty {__version__} [name: {Config().general['name']}] ============")
    print("\nFor gettings started and documentation\nplease read https://github.com/aeon0/botty\n")
    table = BeautifulTable()
    table.set_style(BeautifulTable.STYLE_BOX_ROUNDED)
    table.rows.append([Config().advanced_options['restore_settings_from_backup_key'], "Restore D2R settings from backup"])
    table.rows.append([Config().advanced_options['settings_backup_key'], "Backup D2R current settings"])
    table.rows.append([Config().advanced_options['auto_settings_key'], "Adjust D2R settings"])
    table.rows.append([Config().advanced_options['graphic_debugger_key'], "Start / Stop Graphic debugger"])
    table.rows.append([Config().advanced_options['resume_key'], "Start / Pause Botty"])
    table.rows.append([Config().advanced_options['exit_key'], "Stop bot"])
    table.columns.header = ["hotkey", "action"]
    print(table)
    print("\n")

    keyboard.add_hotkey(Config().advanced_options['auto_settings_key'], lambda: adjust_settings())
    keyboard.add_hotkey(Config().advanced_options['graphic_debugger_key'], lambda: start_or_stop_graphic_debugger(controllers))
    keyboard.add_hotkey(Config().advanced_options['restore_settings_from_backup_key'], lambda: restore_settings_from_backup())
    keyboard.add_hotkey(Config().advanced_options['settings_backup_key'], lambda: backup_settings())
    keyboard.add_hotkey(Config().advanced_options['resume_key'], lambda: start_or_pause_bot(controllers))
    keyboard.add_hotkey(Config().advanced_options["exit_key"], lambda: on_exit())
    keyboard.wait()


if __name__ == "__main__":
    # To avoid cmd just closing down, except any errors and add a input() to the end
    try:
        game_controller = GameController()
        debugger_controller = GraphicDebuggerController()
        main()
    except:
        traceback.print_exc()
    print("Press Enter to exit ...")
    input()
