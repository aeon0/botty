import os
import threading
import time

import keyboard
from cv2 import cv2

from bot import Bot
from config import Config
from death_manager import DeathManager
from game_recovery import GameRecovery
from game_stats import GameStats
from health_manager import HealthManager
from logger import Logger
from messenger import Messenger
from screen import Screen
from utils.misc import kill_thread


class GameController:

    def __init__(self):
        self.screen = None
        self.health_manager = None
        self.death_manager = None
        self.game_recovery = None
        self.game_stats = None

    def run_bot(self, config: Config, pick_corpse: bool = False):
        keyboard.remove_hotkey(config.general['resume_key'])
        # Create global variables if not done yet (id est: first start)
        if not self.screen:
            self.screen = Screen(config.general["monitor"])
        if not self.health_manager:
            # Run health monitor thread
            self.health_manager = HealthManager(self.screen)
            health_monitor_thread = threading.Thread(target=self.health_manager.start_monitor)
            health_monitor_thread.daemon = True
            health_monitor_thread.start()
        if not self.death_manager:
            # Run death monitor thread
            self.death_manager = DeathManager(self.screen)
            death_monitor_thread = threading.Thread(target=self.death_manager.start_monitor)
            death_monitor_thread.daemon = True
            death_monitor_thread.start()
        if not self.game_recovery:
            self.game_recovery = GameRecovery(self.screen, self.death_manager)
        if not self.game_stats:
            self.game_stats = GameStats()
        # Start bot thread
        bot = Bot(self.screen, self.game_stats, pick_corpse)
        bot_thread = threading.Thread(target=bot.start)
        bot_thread.daemon = True
        bot_thread.start()
        # Register that thread to the death and health manager so they can stop the bot thread if needed
        self.death_manager.set_callback(lambda: bot.stop() or kill_thread(bot_thread))
        self.health_manager.set_callback(lambda: bot.stop() or kill_thread(bot_thread))
        self.health_manager.set_belt_manager(bot.get_belt_manager())
        do_restart = False
        keyboard.add_hotkey(config.general['resume_key'], lambda: bot.toggle_pause())
        messenger = Messenger()
        while 1:
            self.health_manager.update_location(bot.get_curr_location())
            max_game_length_reached = self.game_stats.get_current_game_length() > config.general["max_game_length_s"]
            if max_game_length_reached or self.death_manager.died() or self.health_manager.did_chicken():
                # Some debug and logging
                if max_game_length_reached:
                    Logger.info(f"Max game length reached. Attempting to restart {config.general['name']}!")
                    if config.general["info_screenshots"]:
                        cv2.imwrite(
                            "./info_screenshots/info_max_game_length_reached_" + time.strftime(
                                "%Y%m%d_%H%M%S") + ".png",
                            bot._screen.grab())
                elif self.death_manager.died():
                    self.game_stats.log_death()
                elif self.health_manager.did_chicken():
                    self.game_stats.log_chicken()
                bot.stop()
                kill_thread(bot_thread)
                # Try to recover from whatever situation we are and go back to hero selection
                do_restart = self.game_recovery.go_to_hero_selection()
                break
            time.sleep(0.5)
        bot_thread.join()
        if do_restart:
            # Reset flags before running a new bot
            self.death_manager.reset_death_flag()
            self.health_manager.reset_chicken_flag()
            self.game_stats.log_end_game(failed=max_game_length_reached)
            return self.run_bot(config, True)
        else:
            if config.general["info_screenshots"]:
                cv2.imwrite("./info_screenshots/info_could_not_recover_" + time.strftime("%Y%m%d_%H%M%S") + ".png",
                            bot._screen.grab())
            Logger.error(
                f"{config.general['name']} could not recover from a max game length violation. Shutting down everything.")
            if config.general["custom_message_hook"]:
                messenger.send(msg=f"{config.general['name']}: got stuck and can not resume")
            os._exit(1)
