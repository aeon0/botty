import keyboard
import os
from beautifultable import BeautifulTable
import logging
import traceback

from game_controller import GameController
from version import __version__
from utils.graphic_debugger import GraphicDebuggerController
from utils.auto_settings import adjust_settings, backup_settings, restore_settings_from_backup

from config import Config
from logger import Logger

config = Config(print_warnings=True)
game_controller = GameController(config)
debugger_controller = GraphicDebuggerController(config)


def start_or_pause_bot():
    global game_controller
    global debugger_controller
    if GameController.is_running:
        game_controller.toggle_pause_bot()
    else:
        # Kill the debugger if we invoke botty
        debugger_controller.stop()
        game_controller.start()

def start_or_stop_graphic_debugger():
    global game_controller
    global debugger_controller
    if GraphicDebuggerController.is_running:  
        debugger_controller.stop()
    else:
        # Kill botty if we invoke the debugger
        game_controller.stop()
        debugger_controller.start()

def main():
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
    if not os.path.exists("loot_screenshots") and (config.general["loot_screenshots"] or config.general["message_api_type"] == "discord"):
        os.system("mkdir loot_screenshots")

    print(f"============ Botty {__version__} [name: {config.general['name']}] ============")
    print("\nFor gettings started and documentation\nplease read https://github.com/aeon0/botty\n")
    table = BeautifulTable()
    table.rows.append([config.general['restore_settings_from_backup_key'], "Restore D2R settings from backup"])
    table.rows.append([config.general['settings_backup_key'], "Backup D2R current settings"])
    table.rows.append([config.general['auto_settings_key'], "Adjust D2R settings"])
    table.rows.append([config.general['graphic_debugger_key'], "Start / Stop Graphic debugger"])
    table.rows.append([config.general['resume_key'], "Start / Pause Botty"])
    table.rows.append([config.general['exit_key'], "Stop bot"])
    table.columns.header = ["hotkey", "action"]
    print(table)
    print("\n")

    keyboard.add_hotkey(config.general['auto_settings_key'], lambda: adjust_settings(config))
    keyboard.add_hotkey(config.general['graphic_debugger_key'], lambda: start_or_stop_graphic_debugger())
    keyboard.add_hotkey(config.general['restore_settings_from_backup_key'], lambda: restore_settings_from_backup(config))
    keyboard.add_hotkey(config.general['settings_backup_key'], lambda: backup_settings(config))
    keyboard.add_hotkey(config.general['resume_key'], lambda c: start_or_pause_bot(), args=[config])
    keyboard.add_hotkey(config.general["exit_key"], lambda: Logger.info(f'Force Exit') or os._exit(1))
    keyboard.wait()

    """ LEFTOVER FROM DIABLO
    while 1:
        if keyboard.is_pressed(config.general['resume_key']):
            screen = Screen(config.general["monitor"])
            # Run health monitor thread
            health_manager = HealthManager(screen)
            health_monitor_thread = threading.Thread(target=health_manager.start_monitor)
            health_monitor_thread.daemon = True
            health_monitor_thread.start()
            # Run death monitor threadx
            death_manager = DeathManager(screen)
            death_monitor_thread = threading.Thread(target=death_manager.start_monitor)
            death_monitor_thread.daemon = True
            death_monitor_thread.start()
            # Create other "global" instances
            game_recovery = GameRecovery(screen, death_manager)
            game_stats = GameStats()
            run_bot(config, screen, game_recovery, game_stats, death_manager, health_manager)
            break
        if keyboard.is_pressed(config.general['auto_settings_key']):
            adjust_settings()
            break
        elif keyboard.is_pressed(config.general['graphic_debugger_key']):
            run_graphic_debugger()
            break
        time.sleep(0.02)
    """

if __name__ == "__main__":
    # To avoid cmd just closing down, except any errors and add a input() to the end
    try:
        main()
    except:
        traceback.print_exc()
    print("Press Enter to exit ...")
    input()