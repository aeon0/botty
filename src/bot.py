from transitions import Machine
import time
import keyboard
import time
import os
import random
import cv2
from typing import Union

from utils.misc import wait
from game_stats import GameStats
from logger import Logger
from config import Config
from screen import Screen
from template_finder import TemplateFinder
from char import IChar
from item import ItemFinder
from item.pickit import PickIt
from ui import UiManager
from ui import BeltManager
from pather import Pather, Location
from npc_manager import NpcManager
from health_manager import HealthManager
from death_manager import DeathManager
from char.sorceress import Sorceress
from char.trapsin import Trapsin
from char.hammerdin import Hammerdin
from char.barbarian import Barbarian
from run import Pindle, ShenkEld, Trav, Nihlatak
from town import TownManager, A3, A4, A5

# Added for dclone ip hunt
from messenger import Messenger
from utils.dclone_ip import get_d2r_game_ip

class Bot:
    def __init__(self, screen: Screen, game_stats: GameStats, pick_corpse: bool = False):
        self._screen = screen
        self._game_stats = game_stats
        self._messenger = Messenger()
        self._config = Config()
        self._template_finder = TemplateFinder(self._screen)
        self._item_finder = ItemFinder(self._config)
        self._ui_manager = UiManager(self._screen, self._template_finder)
        self._belt_manager = BeltManager(self._screen, self._template_finder)
        self._pather = Pather(self._screen, self._template_finder)
        self._pickit = PickIt(self._screen, self._item_finder, self._ui_manager, self._belt_manager, self._game_stats)

        # Create Character
        if self._config.char["type"] == "sorceress":
            self._char: IChar = Sorceress(self._config.sorceress, self._config.char, self._screen, self._template_finder, self._ui_manager, self._pather)
        elif self._config.char["type"] == "hammerdin":
            self._char: IChar = Hammerdin(self._config.hammerdin, self._config.char, self._screen, self._template_finder, self._ui_manager, self._pather)
        elif self._config.char["type"] == "trapsin":
            self._char: IChar = Trapsin(self._config.trapsin, self._config.char, self._screen, self._template_finder, self._ui_manager, self._pather)
        elif self._config.char["type"] == "barbarian":
            self._char: IChar = Barbarian(self._config.barbarian, self._config.char, self._screen, self._template_finder, self._ui_manager, self._pather)            
        else:
            Logger.error(f'{self._config.char["type"]} is not supported! Closing down bot.')
            os._exit(1)

        # Create Town Manager
        npc_manager = NpcManager(screen, self._template_finder)
        a5 = A5(self._screen, self._template_finder, self._pather, self._char, npc_manager)
        a4 = A4(self._screen, self._template_finder, self._pather, self._char, npc_manager)
        a3 = A3(self._screen, self._template_finder, self._pather, self._char, npc_manager)
        self._town_manager = TownManager(self._template_finder, self._ui_manager, self._item_finder, a3, a4, a5)
        self._route_config = self._config.routes

        # Create runs
        if self._route_config["run_shenk"] and not self._route_config["run_eldritch"]:
            Logger.error("Running shenk without eldtritch is not supported. Either run none or both")
            os._exit(1)
        self._do_runs = {
            "run_trav": self._route_config["run_trav"],
            "run_pindle": self._route_config["run_pindle"],
            "run_shenk": self._route_config["run_shenk"] or self._route_config["run_eldritch"],
            "run_nihlatak": self._route_config["run_nihlatak"],
        }
        if self._config.general["randomize_runs"]:
            self.shuffle_runs()
        self._pindle = Pindle(self._template_finder, self._pather, self._town_manager, self._ui_manager, self._char, self._pickit)
        self._shenk = ShenkEld(self._template_finder, self._pather, self._town_manager, self._ui_manager, self._char, self._pickit)
        self._trav = Trav(self._template_finder, self._pather, self._town_manager, self._ui_manager, self._char, self._pickit)
        self._nihlatak = Nihlatak(self._template_finder, self._pather, self._town_manager, self._ui_manager, self._char, self._pickit)

        # Create member variables
        self._pick_corpse = pick_corpse
        self._picked_up_items = False
        self._curr_loc: Union[bool, Location] = None
        self._tps_left = 10 # assume half full tp book
        self._pre_buffed = False
        self._stopping = False
        self._pausing = False
        self._current_threads = []
        self._no_stash_counter = 0
        self._ran_no_pickup = False

        # Create State Machine
        self._states=['hero_selection', 'town', 'pindle', 'shenk', 'trav', 'nihlatak']
        self._transitions = [
            { 'trigger': 'create_game', 'source': 'hero_selection', 'dest': 'town', 'before': "on_create_game"},
            # Tasks within town
            { 'trigger': 'maintenance', 'source': 'town', 'dest': 'town', 'before': "on_maintenance"},
            # Different runs
            { 'trigger': 'run_pindle', 'source': 'town', 'dest': 'pindle', 'before': "on_run_pindle"},
            { 'trigger': 'run_shenk', 'source': 'town', 'dest': 'shenk', 'before': "on_run_shenk"},
            { 'trigger': 'run_trav', 'source': 'town', 'dest': 'trav', 'before': "on_run_trav"},
            { 'trigger': 'run_nihlatak', 'source': 'town', 'dest': 'nihlatak', 'before': "on_run_nihlatak"},
            # End run / game
            { 'trigger': 'end_run', 'source': ['shenk', 'pindle', 'nihlatak','trav'], 'dest': 'town', 'before': "on_end_run"},
            { 'trigger': 'end_game', 'source': ['town', 'shenk', 'pindle', 'nihlatak', 'trav', 'end_run'], 'dest': 'hero_selection', 'before': "on_end_game"},
        ]
        self.machine = Machine(model=self, states=self._states, initial="hero_selection", transitions=self._transitions, queued=True)

    def draw_graph(self):
        # Draw the whole graph, graphviz binaries must be installed and added to path for this!
        from transitions.extensions import GraphMachine
        self.machine = GraphMachine(model=self, states=self._states, initial="hero_selection", transitions=self._transitions, queued=True)
        self.machine.get_graph().draw('my_state_diagram.png', prog='dot')

    def get_curr_location(self):
        return self._curr_loc

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

    def trigger_or_stop(self, name: str, **kwargs):
        if self._pausing:
            Logger.info(f"{self._config.general['name']} is now pausing")
            self._game_stats.pause_timer()
        while self._pausing:
            time.sleep(0.2)
        if not self._stopping:
            self.trigger(name, **kwargs)

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
        keyboard.release(self._config.char["stand_still"])
        # Start a game from hero selection
        self._game_stats.log_start_game()
        self._template_finder.search_and_wait("D2_LOGO_HS", roi=self._config.ui_roi["hero_selection_logo"])
        if not self._ui_manager.start_game(): return
        self._curr_loc = self._town_manager.wait_for_town_spawn()

        # Check for the current game ip and pause if we are able to obtain the hot ip
        if self._config.dclone["region_ips"] != "" and self._config.dclone["dclone_hotip"] != "":
            cur_game_ip = get_d2r_game_ip()
            hot_ip = self._config.dclone["dclone_hotip"]
            Logger.debug(f"Current Game IP: {cur_game_ip}   and HOTIP: {hot_ip}")
            if hot_ip == cur_game_ip:
                self._messenger.send(msg=f"Dclone IP Found on IP: {cur_game_ip}")
                print("Press Enter")
                input()
                os._exit(1)
            else:
                Logger.info(f"Please Enter the region ip and hot ip on config to use")
            
        # Run /nopickup command to avoid picking up stuff on accident
        if not self._ran_no_pickup:
            self._ran_no_pickup = True
            if self._ui_manager.enable_no_pickup():
                Logger.info("Activated /nopickup")
            else:
                Logger.error("Failed to detect if /nopickup command was applied or not")
        self.trigger_or_stop("maintenance")

    def on_maintenance(self):
        # Handle picking up corpse in case of death
        if self._pick_corpse:
            self._pick_corpse = False
            time.sleep(0.6)
            DeathManager.pick_up_corpse(self._config, self._screen)
            wait(1.2, 1.5)
            self._belt_manager.fill_up_belt_from_inventory(self._config.char["num_loot_columns"])
            wait(0.5)
        # Look at belt to figure out how many pots need to be picked up
        self._belt_manager.update_pot_needs()

        # Check if should need some healing
        img = self._screen.grab()
        if HealthManager.get_health(self._config, img) < 0.6 or HealthManager.get_mana(self._config, img) < 0.2:
            Logger.info("Healing at next possible Vendor")
            self._curr_loc = self._town_manager.heal(self._curr_loc)
            if not self._curr_loc:
                return self.trigger_or_stop("end_game", failed=True)

        # Stash stuff, either when item was picked up or after X runs without stashing because of unwanted loot in inventory
        self._no_stash_counter += 1
        force_stash = self._no_stash_counter > 4 and self._ui_manager.should_stash(self._config.char["num_loot_columns"])
        if self._picked_up_items or force_stash:
            Logger.info("Stashing items")
            self._curr_loc = self._town_manager.stash(self._curr_loc)
            if not self._curr_loc:
                return self.trigger_or_stop("end_game", failed=True)
            self._no_stash_counter = 0
            self._picked_up_items = False
            wait(1.0)

        # Check if we are out of tps or need repairing
        need_repair = self._ui_manager.repair_needed()
        if self._tps_left < random.randint(2, 5) or need_repair:
            if need_repair: Logger.info("Repair needed. Gear is about to break")
            else: Logger.info("Repairing and buying TPs at next Vendor")
            self._curr_loc = self._town_manager.repair_and_fill_tps(self._curr_loc)
            if not self._curr_loc:
                return self.trigger_or_stop("end_game", failed=True)
            self._tps_left = 20
            wait(1.0)

        # Check if merc needs to be revived
        merc_alive = self._template_finder.search(["MERC_A2","MERC_A1","MERC_A5","MERC_A3"], self._screen.grab(), threshold=0.9, roi=self._config.ui_roi["merc_icon"]).valid
        if not merc_alive and self._config.char["use_merc"]:
            Logger.info("Resurrect merc")
            self._game_stats.log_merc_death()
            self._curr_loc = self._town_manager.resurrect(self._curr_loc)
            if not self._curr_loc:
                return self.trigger_or_stop("end_game", failed=True)

        # Start a new run
        started_run = False
        for key in self._do_runs:
            if self._do_runs[key]:
                self.trigger_or_stop(key)
                started_run = True
                break
        if not started_run:
            self.trigger_or_stop("end_game")

    def on_end_game(self, failed: bool = False):
        if self._config.general["info_screenshots"]:
            cv2.imwrite("./info_screenshots/info_failed_game_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        self._curr_loc = False
        self._pre_buffed = False
        self._ui_manager.save_and_exit()
        self._game_stats.log_end_game(failed=failed)
        self._do_runs = {
            "run_trav": self._route_config["run_trav"],
            "run_pindle": self._route_config["run_pindle"],
            "run_shenk": self._route_config["run_shenk"] or self._route_config["run_eldritch"],
            "run_nihlatak": self._route_config["run_nihlatak"],
        }
        if self._config.general["randomize_runs"]:
            self.shuffle_runs()
        wait(0.2, 0.5)
        self.trigger_or_stop("create_game")

    def on_end_run(self):
        if not self._config.char["pre_buff_every_run"]:
            self._pre_buffed = True
        success = self._char.tp_town()
        if success:
            self._tps_left -= 1
            self._curr_loc = self._town_manager.wait_for_tp(self._curr_loc)
            if self._curr_loc:
                return self.trigger_or_stop("maintenance")
        if not self._ui_manager.has_tps():
            self._tps_left = 0
        self.trigger_or_stop("end_game", failed=True)

    # All the runs go here
    # ==================================
    def _ending_run_helper(self, res: Union[bool, tuple[Location, bool]]):
        # either fill member variables with result data or mark run as failed
        failed_run = True
        if res:
            failed_run = False
            self._curr_loc, self._picked_up_items = res
        # in case its the last run or the run was failed, end game, otherwise move to next run
        if self.is_last_run() or failed_run:
            self.trigger_or_stop("end_game", failed=failed_run)
        else:
            self.trigger_or_stop("end_run")

    def on_run_pindle(self):
        res = False
        self._do_runs["run_pindle"] = False
        self._game_stats.update_location("Pindle")
        self._curr_loc = self._pindle.approach(self._curr_loc)
        if self._curr_loc:
            res = self._pindle.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_shenk(self):
        res = False
        self._do_runs["run_shenk"] = False
        self._game_stats.update_location("Shenk")
        self._curr_loc = self._shenk.approach(self._curr_loc)
        if self._curr_loc:
            res = self._shenk.battle(self._route_config["run_shenk"], not self._pre_buffed, self._game_stats)
        self._ending_run_helper(res)

    def on_run_trav(self):
        res = False
        self._do_runs["run_trav"] = False
        self._game_stats.update_location("Travincal")
        self._curr_loc = self._trav.approach(self._curr_loc)
        if self._curr_loc:
            res = self._trav.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_nihlatak(self):
        res = False
        self._do_runs["run_nihlatak"] = False
        self._game_stats.update_location("Nihlatak")
        self._curr_loc = self._nihlatak.approach(self._curr_loc)
        if self._curr_loc:
            res = self._nihlatak.battle(not self._pre_buffed)
        self._ending_run_helper(res)
