from logger import Logger
import time
import threading
from config import Config
from utils.misc import send_discord, hms
import inspect


class GameStats:
    def __init__(self):
        self._config = Config()
        self._picked_up_items = []
        self._start_time = time.time()
        self._timepaused = None
        self._paused = False
        self._timer = None
        self._game_counter = 0
        self._chicken_counter = 0
        self._death_counter = 0
        self._runs_failed = 0

    def _send_discord_thread(self, msg: str):
        if self._config.general["custom_discord_hook"]:
            msg = f"{self._config.general['name']}: {msg}"
            send_discord_thread = threading.Thread(
                target=send_discord,
                args=(msg, self._config.general["custom_discord_hook"])
            )
            send_discord_thread.daemon = True
            send_discord_thread.start()

    def log_item_pickup(self, item_name: str, send_discord: bool):
        self._picked_up_items.append(item_name)
        if send_discord:
            self._send_discord_thread(f"Found {item_name}")

    def log_death(self):
        self._death_counter += 1
        self._send_discord_thread(f"You have died")

    def log_chicken(self):
        self._chicken_counter += 1
        self._send_discord_thread(f"You have chickened")

    def log_start_game(self):
        if self._game_counter > 0:
            self._save_stats_to_file()
            if self._game_counter % 20 == 0:
                # every 20th game send a discord update about current status
                self._send_discord_status_update()
        self._game_counter += 1
        self._timer = time.time()
        Logger.info(f"Starting game #{self._game_counter}")

    def log_end_game(self):
        elapsed_time = time.time() - self._timer
        Logger.info(f"End game. Elapsed time: {elapsed_time:.2f}s")

    def log_failed_run(self):
        self._runs_failed += 1

    def pause_timer(self):
        """ Pauses the timer """
        if self._start_time is None:
            raise ValueError("Timer not started")
        if self._paused:
            raise ValueError("Timer is already paused")
        Logger.info(f'Pausing timer')
        self._timepaused = time.time()
        self._paused = True

    def resume_timer(self):
        """ Resumes the timer by adding the pause time to the start time """
        if self._start_time is None:
            raise ValueError("Timer not started")
        if not self._paused:
            raise ValueError("Timer is not paused")
        Logger.info(f'Resuming timer')
        pausetime = time.time() - self._timepaused
        self._start_time = self._start_time + pausetime
        self._paused = False

    def get_current_game_length(self):        
        if self._start_time is None:
            return 0
        if self._paused:
            return self._timepaused - self._start_time
        else:
            return time.time() - self._start_time

    def _create_msg(self):
        elapsed_time = time.time() - self._start_time
        elapsed_time_str = hms(elapsed_time)
        avg_length_str = "n/a"
        if self._game_counter > 0:
            avg_length = elapsed_time / float(self._game_counter)
            avg_length_str = hms(avg_length)
        msg = inspect.cleandoc(f'''
            Session length: {elapsed_time_str}
            Games: {self._game_counter}
            Avg Game Length: {avg_length_str}
            Chickens: {self._chicken_counter}
            Deaths: {self._death_counter}
            Failed runs: {self._runs_failed}
        ''')
        return msg

    def _send_discord_status_update(self):
        msg = f"Status Report\n{self._create_msg()}\nVersion:"
        self._send_discord_thread(msg)

    def _save_stats_to_file(self):
        msg = self._create_msg()
        msg += "\nItems:"
        for item_name in self._picked_up_items:
            msg += f"\n  {item_name}"
        with open("stats.log", "w+") as f:
            f.write(msg)


if __name__ == "__main__":
    game_stats = GameStats()
    game_stats._send_discord_status_update()
    game_stats._save_stats_to_file()
