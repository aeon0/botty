from transitions import Machine
import time
from char.hammerdin import Hammerdin
from template_finder import TemplateFinder
from item_finder import ItemFinder
from screen import Screen
from ui_manager import UiManager
from belt_manager import BeltManager
from pather import Pather, Location
from logger import Logger
from char.sorceress import Sorceress
from char.i_char import IChar
from config import Config
from health_manager import HealthManager
from death_manager import DeathManager
from npc_manager import NpcManager, Npc
from pickit import PickIt
from game_stats import GameStats
from utils.misc import wait
import keyboard
import time
import os
import random


class Bot:
    def __init__(self, screen: Screen, game_stats: GameStats, pick_corpse: bool = False):
        self._screen = screen
        self._game_stats = game_stats
        self._pick_corpse = pick_corpse
        self._config = Config()
        self._template_finder = TemplateFinder(self._screen)
        self._item_finder = ItemFinder()
        self._ui_manager = UiManager(self._screen, self._template_finder)
        self._belt_manager = BeltManager(self._screen, self._template_finder)
        self._pather = Pather(self._screen, self._template_finder)
        self._npc_manager = NpcManager(self._screen, self._template_finder)
        self._pickit = PickIt(self._screen, self._item_finder, self._ui_manager, self._belt_manager, self._game_stats)
        if self._config.char["type"] == "sorceress":
            self._char: IChar = Sorceress(self._config.sorceress, self._config.char, self._screen, self._template_finder, self._ui_manager, self._pather)
        elif self._config.char["type"] == "hammerdin":
            self._char: IChar = Hammerdin(self._config.hammerdin, self._config.char, self._screen, self._template_finder, self._ui_manager, self._pather)
        else:
            Logger.error(f'{self._config.char["type"]} is not supported! Closing down bot.')
            os._exit(1)
        self._route_config = self._config.routes
        if self._route_config["run_shenk"] and not self._route_config["run_eldritch"]:
            Logger.error("Running shenk without eldtritch is not supported. Either run none, both or eldritch only.")
            os._exit(1)
        self._do_runs = {
            "run_pindle": self._route_config["run_pindle"],
            "run_shenk": self._route_config["run_shenk"] or self._route_config["run_eldritch"],
        }
        if self._config.general["randomize_runs"]:
            self.shuffle_runs()
        self._picked_up_items = False
        self._tp_is_up = False
        self._curr_location: Location = None
        self._tps_left = 20
        self._pre_buffed = 0
        self._stopping = False
        self._pausing = False
        self._current_threads = []
        self._no_stash_counter = 0

        self._states=['hero_selection', 'a5_town', 'pindle', 'shenk']
        self._transitions = [
            { 'trigger': 'create_game', 'source': 'hero_selection', 'dest': 'a5_town', 'before': "on_create_game"},
            # Tasks within town
            { 'trigger': 'maintenance', 'source': 'a5_town', 'dest': 'a5_town', 'before': "on_maintenance"},
            # Different runs
            { 'trigger': 'run_pindle', 'source': 'a5_town', 'dest': 'pindle', 'before': "on_run_pindle"},
            { 'trigger': 'run_shenk', 'source': 'a5_town', 'dest': 'shenk', 'before': "on_run_shenk"},
            # End run / game
            { 'trigger': 'end_run', 'source': ['shenk', 'pindle'], 'dest': 'a5_town', 'before': "on_end_run"},
            { 'trigger': 'end_game', 'source': ['a5_town', 'shenk', 'pindle', 'end_run'], 'dest': 'hero_selection', 'before': "on_end_game"},
        ]
        self.machine = Machine(model=self, states=self._states, initial="hero_selection", transitions=self._transitions, queued=True)

    def draw_graph(self):
        # Draw the whole graph, graphviz binaries must be installed and added to path for this!
        from transitions.extensions import GraphMachine
        self.machine = GraphMachine(model=self, states=self._states, initial="hero_selection", transitions=self._transitions, queued=True)
        self.machine.get_graph().draw('my_state_diagram.png', prog='dot')

    def get_curr_location(self):
        return self._curr_location

    def start(self):
        self.trigger('create_game')

    def stop(self):
        self._stopping = True

    def toggle_pause(self):
        self._pausing = not self._pausing
        if self._pausing:
            Logger.info(f"Pause at next state change...") 
        else:
            Logger.info(f"Resume")
            self._game_stats.resume_timer()

    def trigger_or_stop(self, name: str):
        if self._pausing:
            Logger.info(f"{self._config.general['name']} is now pausing")
            self._game_stats.pause_timer()
        while self._pausing:
            time.sleep(0.2)
        if not self._stopping:
            self.trigger(name)

    def current_game_length(self):
        return self._game_stats.get_current_game_length()

    def shuffle_runs(self):
        tmp = list(self._do_runs.items())
        random.shuffle(tmp)
        self._do_runs = dict(tmp)

    def is_last_run(self):
        found_unfinished_run = False
        for key in self._do_runs:
            if self._do_runs[key]:
                found_unfinished_run = True
                break
        return not found_unfinished_run

    def on_create_game(self):
        self._game_stats.log_start_game()
        template_match = self._template_finder.search_and_wait("D2_LOGO_HS", roi=self._config.ui_roi["hero_selection_logo"])
        if template_match.valid:
            Logger.debug(f"Found {template_match.name}")
        if not self._ui_manager.start_game():
            return
        self._template_finder.search_and_wait(["A5_TOWN_1", "A5_TOWN_0"])
        self._tp_is_up = False
        self._curr_location = Location.A5_TOWN_START
        # Make sure these keys are released
        keyboard.release(self._config.char["stand_still"])
        wait(0.05, 0.15)
        keyboard.release(self._config.char["show_items"])
        self.trigger_or_stop("maintenance")

    def on_maintenance(self):
        if self._pick_corpse:
            self._pick_corpse = False
            time.sleep(0.6)
            DeathManager.pick_up_corpse(self._config, self._screen)
            wait(1.2, 1.5)
            self._belt_manager.fill_up_belt_from_inventory(self._config.char["num_loot_columns"])

        self._belt_manager.update_pot_needs()

        # Check if healing is needed, TODO: add shoping e.g. for potions
        img = self._screen.grab()
        # TODO: If tp is up we always go back into the portal...
        if not self._tp_is_up and (HealthManager.get_health(self._config, img) < 0.6 or HealthManager.get_mana(self._config, img) < 0.3):
            Logger.info("Need some healing first. Going to Malah.")
            if not self._pather.traverse_nodes(self._curr_location, Location.MALAH, self._char):
                self.trigger_or_stop("end_game")
                return
            self._curr_location = Location.MALAH
            self._npc_manager.open_npc_menu(Npc.MALAH)
            if not self._pather.traverse_nodes(self._curr_location, Location.A5_TOWN_START, self._char):
                self.trigger_or_stop("end_game")
                return
            self._curr_location = Location.A5_TOWN_START

        # Stash stuff, either when item was picked up or after 4 runs without stashing (so unwanted loot will not cause inventory full)
        # but should not happen much with /nopickup set
        self._no_stash_counter += 1
        if self._picked_up_items or (self._no_stash_counter > 4 and self._ui_manager.should_stash(self._config.char["num_loot_columns"])):
            self._no_stash_counter = 0
            Logger.info("Stashing picked up items.")
            if not self._pather.traverse_nodes(self._curr_location, Location.A5_STASH, self._char):
                self.trigger_or_stop("end_game")
                return
            self._curr_location = Location.A5_STASH
            time.sleep(0.3)
            stash_is_open_func = lambda: self._template_finder.search("INVENTORY_GOLD_BTN", self._screen.grab(), roi=self._config.ui_roi["gold_btn"]).valid
            if self._char.select_by_template("A5_STASH", stash_is_open_func):
                self._ui_manager.stash_all_items(self._config.char["num_loot_columns"], self._item_finder)
                self._picked_up_items = False
                time.sleep(1.2) # otherwise next grab of screen will still have inventory
            else:
                Logger.warning("Could not find stash, continue...")

        if self._tps_left < 3 or (self._config.char["tp"] and not self._ui_manager.has_tps()):
            Logger.info("Repairing and buying TPs at Larzuk.")
            if not self._pather.traverse_nodes(self._curr_location, Location.LARZUK, self._char):
                self.trigger_or_stop("end_game")
                return
            self._curr_location = Location.LARZUK
            self._npc_manager.open_npc_menu(Npc.LARZUK)
            self._npc_manager.press_npc_btn(Npc.LARZUK, "trade_repair")
            if self._ui_manager.repair_and_fill_up_tp():
                wait(0.1, 0.2)
                self._ui_manager.close_vendor_screen()
                self._tps_left = 20
            wait(0.5)

        # Check if merc needs to be revived
        merc_alive = self._template_finder.search("MERC", self._screen.grab(), threshold=0.9, roi=[0, 0, 200, 200]).valid
        if not merc_alive:
            Logger.info("Reviving merc.")
            if not self._pather.traverse_nodes(self._curr_location, Location.QUAL_KEHK, self._char):
                self.trigger_or_stop("end_game")
                return
            self._curr_location = Location.QUAL_KEHK
            if self._npc_manager.open_npc_menu(Npc.QUAL_KEHK):
                self._npc_manager.press_npc_btn(Npc.QUAL_KEHK, "resurrect")
            time.sleep(1.2)

        # Start a new run
        started_run = False
        for key in self._do_runs:
            if self._do_runs[key]:
                self.trigger_or_stop(key)
                started_run = True
                break
        if not started_run:
            self.trigger_or_stop("end_game")

    def on_run_pindle(self):
        def do_it() -> bool:
            Logger.info("Run Pindle")
            if not self._pather.traverse_nodes(self._curr_location, Location.NIHLATHAK_PORTAL, self._char): return False
            self._curr_location = Location.NIHLATHAK_PORTAL
            wait(0.3, 0.4) # otherwise will often missclick because still moving
            found_loading_screen_func = lambda: self._ui_manager.wait_for_loading_screen(2.0)
            if not self._char.select_by_template(["A5_RED_PORTAL", "A5_RED_PORTAL_TEXT"], found_loading_screen_func): return False
            self._curr_location = Location.PINDLE_START
            if not self._template_finder.search_and_wait(["PINDLE_0", "PINDLE_1"], threshold=0.65, time_out=20).valid: return False
            if not self._pre_buffed:
                self._char.pre_buff()
                self._pre_buffed = 1
            if self._config.char["static_path_pindle"]:
                self._pather.traverse_nodes_fixed("pindle_save_dist", self._char)
            else:
                if not self._pather.traverse_nodes(Location.PINDLE_START, Location.PINDLE_SAVE_DIST, self._char): return False
            self._char.kill_pindle()
            self._picked_up_items = self._pickit.pick_up_items(self._char)
            return True

        self._do_runs["run_pindle"] = False
        success = do_it()
        if self.is_last_run() or not success:
            self.trigger_or_stop("end_game")
        else:
            self.trigger_or_stop("end_run")

    def on_run_shenk(self):
        def do_it():
            Logger.info("Run Eldritch")
            if not self._pather.traverse_nodes(self._curr_location, Location.A5_WP, self._char): return False
            self._curr_location = Location.A5_WP
            wait(0.5, 0.7) # otherwise will missclick because still moving
            found_wp_func = lambda: self._template_finder.search("WAYPOINT_MENU", self._screen.grab()).valid
            if not self._char.select_by_template("A5_WP", found_wp_func): return False
            self._ui_manager.use_wp(4, 1)
            # eldritch
            self._curr_location = Location.ELDRITCH_START
            if not self._template_finder.search_and_wait(["ELDRITCH_0", "ELDRITCH_START"], threshold=0.65, time_out=20).valid: return False
            if not self._pre_buffed:
                self._char.pre_buff()
                self._pre_buffed = 1
            if self._config.char["static_path_eldritch"]:
                self._pather.traverse_nodes_fixed("eldritch_save_dist", self._char)
            else:
                if not self._pather.traverse_nodes(Location.ELDRITCH_START, Location.ELDRITCH_SAVE_DIST, self._char): return False
            self._char.kill_eldritch()
            self._picked_up_items = self._pickit.pick_up_items(self._char)
            # shenk
            if self._route_config["run_shenk"]:
                Logger.info("Run Shenk")
                self._curr_location = Location.SHENK_START
                if not self._pather.traverse_nodes(Location.SHENK_START, Location.SHENK_SAVE_DIST, self._char): return False
                self._char.kill_shenk()
                wait(1.9, 2.4) # sometimes merc needs some time to kill shenk...
                self._picked_up_items |= self._pickit.pick_up_items(self._char)
            return True

        self._do_runs["run_shenk"] = False
        success = do_it()
        if self.is_last_run() or not success:
            self.trigger_or_stop("end_game")
        else:
            self.trigger_or_stop("end_run")

    def on_end_game(self):
        self._pre_buffed = 0
        self._ui_manager.save_and_exit()
        self._game_stats.log_end_game()
        self._do_runs = {
            "run_pindle": self._route_config["run_pindle"],
            "run_shenk": self._route_config["run_shenk"] or self._route_config["run_eldritch"]
        }
        if self._config.general["randomize_runs"]:
            self.shuffle_runs()
        wait(0.2, 0.5)
        self.trigger_or_stop("create_game")

    def on_end_run(self):
        success = self._char.tp_town()
        if success:
            self._tps_left -= 1
            success = self._template_finder.search_and_wait(["A5_TOWN_1", "A5_TOWN_0"], time_out=10).valid
            if success:
                self._tp_is_up = True
                self._curr_location = Location.A5_TOWN_START
                self.trigger_or_stop("maintenance")
            else:
                self.trigger_or_stop("end_game")
        else:
            self._tps_left = 0
            self.trigger_or_stop("end_game")


if __name__ == "__main__":
    import keyboard
    keyboard.add_hotkey("f12", lambda: os._exit(1))
    keyboard.wait("f11")
    config = Config()
    screen = Screen(config.general["monitor"])
    bot = Bot(screen)
    bot.state = "a5_town"
    bot._curr_location = Location.A5_TOWN_START
    bot.on_maintenance()
