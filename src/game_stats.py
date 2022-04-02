import numpy as np
import time
from logger import Logger
from config import Config
from utils.levels import get_level
from version import __version__
from ui import player_bar
from bot_events import hook


class GameStats:
    def __init__(self):
        self._start_time = time.time()
        self._timer = None
        self._timepaused = None
        self._paused = False
        self._game_counter = 0
        self._chicken_counter = 0
        self._death_counter = 0
        self._merc_death_counter = 0
        self._runs_failed = 0
        self._run_counter = 1
        self._consecutive_runs_failed = 0
        self._failed_game_time = 0
        self._location = None
        self._location_stats = {}
        self._location_stats["totals"] = { "items": 0, "runs": 0, "deaths": 0, "chickens": 0, "merc_deaths": 0, "failed_runs": 0 }
        self._stats_filename = f'stats_{time.strftime("%Y%m%d_%H%M%S")}.log'
        self._nopickup_active = False
        self._starting_exp = 0
        self._current_exp = 0
        self._current_lvl = 0


    def update_location(self, loc: str):
        if self._location != loc:
            self._location = str(loc)
            self.populate_location_stat()

    def populate_location_stat(self):
        if self._location not in self._location_stats:
            self._location_stats[self._location] = { "items": [], "deaths": 0, "chickens": 0, "merc_deaths": 0, "failed_runs": 0 }

    def log_item_keep(self, item_name: str, send_message: bool, img: np.ndarray, ocr_text: str = None):
        Logger.debug(f"Stashed and logged: {item_name}")
        filtered_items = ["_potion", "misc_gold"]
        if self._location is not None and not any(substring in item_name for substring in filtered_items):
            self._location_stats[self._location]["items"].append(item_name)
            self._location_stats["totals"]["items"] += 1

        hook.Call("on_item_keep", item_name=item_name, img=img, location=self._location, ocr_text=ocr_text, send_message=send_message, instance=self)
        

    def log_death(self, img: str):
        self._death_counter += 1
        if self._location is not None:
            self._location_stats[self._location]["deaths"] += 1
            self._location_stats["totals"]["deaths"] += 1

        hook.Call("on_death", count=self._death_counter, location=self._location, img=img, instance=self)


    def log_chicken(self, img: str):
        self._chicken_counter += 1
        if self._location is not None:
            self._location_stats[self._location]["chickens"] += 1
            self._location_stats["totals"]["chickens"] += 1
            
        hook.Call("on_chicken", count=self._chicken_counter, location=self._location, instance=self)

    def log_merc_death(self):
        self._merc_death_counter += 1
        if self._location is not None:
            self._location_stats[self._location]["merc_deaths"] += 1
            self._location_stats["totals"]["merc_deaths"] += 1

        hook.Call("on_merc_death", count=self._merc_death_counter, location=self._location, instance=self)
        

    def log_start_game(self):
        self._timer = time.time()
        self._game_counter += 1
        self._location_stats["totals"]["runs"] += 1
        Logger.info(f"Starting game #{self._game_counter}")

        hook.Call("on_run", 
            runs=self._game_counter, 
            deaths=self._death_counter, 
            chickens=self._chicken_counter, 
            merc_deaths=self._merc_death_counter, 
            failed_runs=self._runs_failed,
            items=self._location_stats["totals"]["items"],
            location=self._location,
            location_stats=self._location_stats,
            instance=self
        )


    def log_end_game(self, failed: bool = False):
        elapsed_time = 0
        if self._timer is not None:
            elapsed_time = time.time() - self._timer
        self._timer = None
        if failed:
            self._runs_failed += 1
            self._consecutive_runs_failed += 1
            if self._location is not None:
                self._location_stats[self._location]["failed_runs"] += 1
                self._location_stats["totals"]["failed_runs"] += 1
            self._failed_game_time += elapsed_time
            Logger.warning(f"End failed game: Elapsed time: {elapsed_time:.2f}s Fails: {self._consecutive_runs_failed}")
            hook.Call("on_failed_run", count=self._runs_failed, consecutive_count=self._consecutive_runs_failed, instance=self)
        else:
            self._consecutive_runs_failed = 0
            
            Logger.info(f"End game. Elapsed time: {elapsed_time:.2f}s")

    def log_exp(self):
        exp = player_bar.get_experience()

        if exp[1] > 0:
            curr_lvl = get_level(exp[1])['lvl']
            if curr_lvl > 0:
                self._current_lvl = curr_lvl-1
                
        
        if self._starting_exp == 0:
            self._starting_exp = exp[0]
        
        if exp[0] > 0:
            self._current_exp = exp[0]

    def pause_timer(self):
        if self._timer is None or self._paused:
            return
        self._timepaused = time.time()
        self._paused = True
        hook.Call("on_pause", paused=self._paused)


    def resume_timer(self):
        if self._timer is None or not self._paused:
            return
        pausetime = time.time() - self._timepaused
        self._timer = self._timer + pausetime
        self._paused = False
        hook.Call("on_resume", paused=self._paused)

    def get_current_game_length(self):
        if self._timer is None:
            return 0
        if self._paused:
            return self._timepaused - self._timer
        else:
            return time.time() - self._timer

    def get_consecutive_runs_failed(self):
        return self._consecutive_runs_failed


if __name__ == "__main__":
    game_stats = GameStats()
    game_stats.log_item_keep("rune_12", True)
    game_stats._save_stats_to_file()
