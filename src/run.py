from bot import Bot
from game_recovery import GameRecovery
from game_stats import GameStats
from health_manager import HealthManager
from death_manager import DeathManager
from screen import Screen
from logger import Logger
import keyboard
import os
from config import Config
from utils.graphic_debugger import run_graphic_debugger
from version import __version__
from utils.auto_settings import adjust_settings
from utils.misc import kill_thread, send_discord
import threading
from beautifultable import BeautifulTable
import time
import logging
import cv2
import traceback


def run_bot(
    config: Config,
    screen: Screen,
    game_recovery: GameRecovery,
    game_stats: GameStats,
    death_manager: DeathManager,
    health_manager: HealthManager,
    pick_corpse: bool = False
):
    # Start bot thread
    bot = Bot(screen, game_stats, pick_corpse)
    bot_thread = threading.Thread(target=bot.start)
    bot_thread.daemon = True
    bot_thread.start()
    # Register that thread to the death and health manager so they can stop the bot thread if needed
    death_manager.set_callback(lambda: bot.stop() or kill_thread(bot_thread))
    health_manager.set_callback(lambda: bot.stop() or kill_thread(bot_thread))
    do_restart = False
    keyboard.add_hotkey(config.general["exit_key"], lambda: Logger.info(f'Force Exit') or os._exit(1))
    keyboard.add_hotkey(config.general['resume_key'], lambda: bot.toggle_pause())
    while 1:
        health_manager.update_location(bot.get_curr_location())
        max_game_length_reached = game_stats.get_current_game_length() > config.general["max_game_length_s"]
        if max_game_length_reached or death_manager.died() or health_manager.did_chicken():
            # Some debug and logging
            if max_game_length_reached:
                Logger.info(f"Max game length reached. Attempting to restart {config.general['name']}!")
                if config.general["info_screenshots"]:
                    cv2.imwrite("./info_screenshots/info_max_game_length_reached_" + time.strftime("%Y%m%d_%H%M%S") + ".png", bot._screen.grab())
            elif death_manager.died():
                game_stats.log_death()
            elif health_manager.did_chicken():
                game_stats.log_chicken()
            bot.stop()
            kill_thread(bot_thread)
            # Try to recover from whatever situation we are and go back to hero selection
            do_restart = game_recovery.go_to_hero_selection()
            break
        time.sleep(0.5)
    bot_thread.join()
    if do_restart:
        # Reset flags before running a new bot
        death_manager.reset_death_flag()
        health_manager.reset_chicken_flag()
        game_stats.log_end_game()
        return run_bot(config, screen, game_recovery, game_stats, death_manager, health_manager, True)
    else:
        if config.general["info_screenshots"]:
            cv2.imwrite("./info_screenshots/info_could_not_recover_" + time.strftime("%Y%m%d_%H%M%S") + ".png", bot._screen.grab())
        Logger.error(f"{config.general['name']} could not recover from a max game length violation. Shutting down everything.")
        if config.general["custom_discord_hook"]:
            send_discord(f"{config.general['name']} got stuck and can not resume", config.general["custom_discord_hook"])
        os._exit(1)

def main():
    config = Config(print_warnings=True)
    if config.general["logg_lvl"] == "info":
        Logger.init(logging.INFO)
    elif config.general["logg_lvl"] == "debug":
        Logger.init(logging.DEBUG)
    else:
        print(f"ERROR: Unkown logg_lvl {config.general['logg_lvl']}. Must be one of [info, debug]")

    # Create folder for debug screenshots if they dont exist yet
    if not os.path.exists("info_screenshots"):
        os.system("mkdir info_screenshots")
    if not os.path.exists("loot_screenshots"):
        os.system("mkdir loot_screenshots")

    keyboard.add_hotkey(config.general["exit_key"], lambda: Logger.info(f'Force Exit') or os._exit(1))

    print(f"============ Botty {__version__} [name: {config.general['name']}] ============")
    print("\nFor gettings started and documentation\nplease read https://github.com/aeon0/botty\n")
    table = BeautifulTable()
    table.rows.append([config.general['auto_settings_key'], "Adjust D2R settings"])
    table.rows.append([config.general['graphic_debugger_key'], "Graphic debugger"])
    table.rows.append([config.general['resume_key'], "Start / Pause Botty"])
    table.rows.append([config.general['exit_key'], "Stop bot"])
    table.columns.header = ["hotkey", "action"]
    print(table)
    print("\n")

    while 1:
        if keyboard.is_pressed(config.general['resume_key']):
            screen = Screen(config.general["monitor"])
            # Run health monitor thread
            health_manager = HealthManager(screen)
            health_monitor_thread = threading.Thread(target=health_manager.start_monitor)
            health_monitor_thread.daemon = True
            health_monitor_thread.start()
            # Run death monitor thread
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


if __name__ == "__main__":
    # To avoid cmd just closing down, except any errors and add a input() to the end
    try:
        main()
    except:
        traceback.print_exc()
    print("Press Enter to exit ...")
    input()
