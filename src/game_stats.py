from logger import Logger
import time
import threading
from config import Config
from messenger import Messenger
from utils.misc import hms
import inspect

from version import __version__


class GameStats:
    def __init__(self):
        self._config = Config()
        self._messenger = Messenger()
        self._picked_up_items = []
        self._start_time = time.time()
        self._timer = None
        self._timepaused = None
        self._paused = False
        self._game_counter = 0
        self._chicken_counter = 0
        self._death_counter = 0
        self._merc_death_counter = 0
        self._runs_failed = 0
        self._failed_game_time = 0
        self._location = None
        
    def update_location(self, loc: str):
        if self._location != loc:
            self._location = str(loc)
            
    def get_location_msg(self):
        if self._location is not None:
            return f" at {self._location}"
        else: 
            return ""

    def _send_message_thread(self, msg: str):
        if self._config.general["custom_message_hook"]:
            send_message_thread = threading.Thread(
                target=self._messenger.send,
                kwargs={"msg": msg}
            )
            send_message_thread.daemon = True
            send_message_thread.start()

    def log_item_pickup(self, item_name: str, send_message: bool):
        self._picked_up_items.append(item_name)
        if send_message:
            msg = f"{self._config.general['name']}: Found {item_name}{self.get_location_msg()}"
            self._send_message_thread(msg)

    def log_death(self):
        self._death_counter += 1
        msg = f"{self._config.general['name']}: You have died{self.get_location_msg()}"
        self._send_message_thread(msg)

    def log_chicken(self):
        self._chicken_counter += 1
        msg = f"{self._config.general['name']}: You have chickened{self.get_location_msg()}"
        self._send_message_thread(msg)

    def log_merc_death(self):
            self._merc_death_counter += 1
            self._send_message_thread(f"{self._config.general['name']}: Merc has died")

    def log_start_game(self):
        if self._game_counter > 0:
            self._save_stats_to_file()
            if self._config.general["discord_status_count"] and self._game_counter % self._config.general["discord_status_count"] == 0:
                # every 20th game send a message update about current status
                self._send_status_update()
        self._game_counter += 1
        self._timer = time.time()
        Logger.info(f"Starting game #{self._game_counter}")

    def log_end_game(self, failed: bool = False):
        elapsed_time = 0
        if self._timer is not None:
            elapsed_time = time.time() - self._timer
        self._timer = None
        if failed:
            self._runs_failed += 1
            self._failed_game_time += elapsed_time
            Logger.warning(f"End failed game: Elpased time: {elapsed_time:.2f}s")
        else:
            Logger.info(f"End game. Elapsed time: {elapsed_time:.2f}s")

    def pause_timer(self):
        if self._timer is None or self._paused:
            return
        self._timepaused = time.time()
        self._paused = True

    def resume_timer(self):
        if self._timer is None or not self._paused:
            return
        pausetime = time.time() - self._timepaused
        self._timer = self._timer + pausetime
        self._paused = False

    def get_current_game_length(self):
        if self._timer is None:
            return 0
        if self._paused:
            return self._timepaused - self._timer
        else:
            return time.time() - self._timer

    def _create_msg(self):
        elapsed_time = time.time() - self._start_time
        elapsed_time_str = hms(elapsed_time)
        avg_length_str = "n/a"
        good_games_count = self._game_counter - self._runs_failed
        if good_games_count > 0:
            good_games_time = elapsed_time - self._failed_game_time
            avg_length = good_games_time / float(good_games_count)
            avg_length_str = hms(avg_length)
        msg = inspect.cleandoc(f'''
            Session length: {elapsed_time_str}
            Games: {self._game_counter}
            Avg Game Length: {avg_length_str}
            Chickens: {self._chicken_counter}
            Deaths: {self._death_counter}
            Merc deaths: {self._merc_death_counter}
            Failed runs: {self._runs_failed}
        ''')
        return msg

    def _send_status_update(self):
        msg = f"{self._config.general['name']}: Status Report\\n{self._create_msg()}\\nVersion: {__version__}"
        self._send_message_thread(msg)

    def _save_stats_to_file(self):
        msg = self._create_msg()
        msg += "\nItems:"
        for item_name in self._picked_up_items:
            msg += f"\n  {item_name}"
        with open("stats.log", "w+") as f:
            f.write(msg)


if __name__ == "__main__":
    game_stats = GameStats()
    game_stats.log_item_pickup("rune_12", True)
