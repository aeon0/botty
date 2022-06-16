import threading
import time
import cv2

from utils.auto_settings import check_settings
from bot import Bot
from config import Config
from death_manager import DeathManager
from game_recovery import GameRecovery
from game_stats import GameStats
from health_manager import HealthManager
from logger import Logger
from messages import Messenger
from screen import grab, get_offset_state
from utils.restart import restart_game, safe_exit
from utils.misc import kill_thread, set_d2r_always_on_top, restore_d2r_window_visibility


class GameController:
    def __init__(self):
        self.is_running = False
        self.health_monitor_thread = None
        self.health_manager = None
        self.death_manager = None
        self.death_monitor_thread = None
        self.game_recovery = None
        self.game_stats = None
        self.game_controller_thread = None
        self.bot_thread = None
        self.bot = None

    def run_bot(self):
        # Start bot thread
        self.bot = Bot(self.game_stats)
        self.bot_thread = threading.Thread(target=self.bot.start)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        # Register that thread to the death and health manager so they can stop the bot thread if needed
        self.death_manager.set_callback(lambda: self.bot.stop() or kill_thread(self.bot_thread))
        self.health_manager.set_callback(lambda: self.bot.stop() or kill_thread(self.bot_thread))
        do_restart = False
        messenger = Messenger()
        force_stopped = False
        while 1:
            max_game_length_reached = self.game_stats.get_current_game_length() > Config().general["max_game_length_s"]
            max_consecutive_fails_reached = False if not Config().general["max_consecutive_fails"] else self.game_stats.get_consecutive_runs_failed() >= Config().general["max_consecutive_fails"]
            if max_game_length_reached or max_consecutive_fails_reached or self.death_manager.died() or self.health_manager.did_chicken() or (force_stopped := self.bot._stopping):
                # Some debug and logging
                if max_game_length_reached:
                    Logger.info(f"Max game length reached. Attempting to restart {Config().general['name']}!")
                    if Config().general["info_screenshots"]:
                        cv2.imwrite("./log/screenshots/info/info_max_game_length_reached_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                elif self.death_manager.died():
                    self.game_stats.log_death(self.death_manager._last_death_screenshot)
                elif self.health_manager.did_chicken():
                    self.game_stats.log_chicken(self.health_manager._last_chicken_screenshot)
                self.bot.stop()
                kill_thread(self.bot_thread)
                # Try to recover from whatever situation we are and go back to hero selection
                if max_consecutive_fails_reached:
                    msg = f"Consecutive fails {self.game_stats.get_consecutive_runs_failed()} >= Max {Config().general['max_consecutive_fails']}. Quitting botty."
                    Logger.error(msg)
                    if messenger.enabled:
                        messenger.send_message(msg)
                    safe_exit(1)
                else:
                    do_restart = self.game_recovery.go_to_hero_selection()
                break
            time.sleep(0.5)
        self.bot_thread.join()
        if do_restart:
            # Reset flags before running a new bot
            self.death_manager.reset_death_flag()
            self.health_manager.reset_chicken_flag()
            self.game_stats.log_end_game(failed = (max_game_length_reached or force_stopped))
            return self.run_bot()
        else:
            if Config().general["info_screenshots"]:
                cv2.imwrite("./log/screenshots/info/info_could_not_recover_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
            if Config().general['restart_d2r_when_stuck']:
                Logger.error("Could not recover from a max game length violation. Restarting the Game.")
                if messenger.enabled:
                    messenger.send_message("Got stuck and will now restart D2R")
                if restart_game(Config().general["d2r_path"], Config().advanced_options["launch_options"]):
                    self.game_stats.log_end_game(failed=max_game_length_reached)
                    if self.setup_screen():
                        self.start_health_manager_thread()
                        self.start_death_manager_thread()
                        self.game_recovery = GameRecovery(self.death_manager)
                        return self.run_bot()
                Logger.error("Could not restart the game. Quitting.")
                if messenger.enabled:
                    messenger.send_message("Got stuck and could not restart the game. Quitting.")
            else:
                Logger.error("Could not recover from a max game length violation. Quitting botty.")
                if messenger.enabled:
                    messenger.send_message("Got stuck and will now quit botty")
            safe_exit(1)

    def start(self):
        # Check if we user should update the d2r settings
        diff = check_settings()
        if len(diff) > 0:
            Logger.warning("Your D2R settings differ from the requiered ones. Please use Auto Settings to adjust them. The differences are:")
            Logger.warning(f"{diff}")
        set_d2r_always_on_top()
        self.setup_screen()
        self.start_health_manager_thread()
        self.start_death_manager_thread()
        self.game_recovery = GameRecovery(self.death_manager)
        self.game_stats = GameStats()
        self.start_game_controller_thread()
        self.is_running = True

    def stop(self):
        restore_d2r_window_visibility()
        if self.death_monitor_thread: kill_thread(self.death_monitor_thread)
        if self.health_monitor_thread: kill_thread(self.health_monitor_thread)
        if self.bot_thread: kill_thread(self.bot_thread)
        if self.game_controller_thread: kill_thread(self.game_controller_thread)
        self.is_running = False

    def setup_screen(self):
        if get_offset_state():
            return True
        return False

    def start_health_manager_thread(self):
        # Run health monitor thread
        self.health_manager = HealthManager()
        self.health_monitor_thread = threading.Thread(target=self.health_manager.start_monitor)
        self.health_monitor_thread.daemon = True
        self.health_monitor_thread.start()

    def start_death_manager_thread(self):
        # Run death monitor thread
        self.death_manager = DeathManager()
        self.death_monitor_thread = threading.Thread(target=self.death_manager.start_monitor)
        self.death_monitor_thread.daemon = True
        self.death_monitor_thread.start()

    def start_game_controller_thread(self):
        # Run game controller thread
        self.game_controller_thread = threading.Thread(target=self.run_bot)
        self.game_controller_thread.daemon = False
        self.game_controller_thread.start()

    def toggle_pause_bot(self):
        if self.bot:
            self.bot.toggle_pause()
