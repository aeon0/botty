from transitions import Machine
import time
import keyboard
import time
import os
import random
import cv2
from copy import copy
from typing import Union
from collections import OrderedDict

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
from ui import InventoryManager
from pather import Pather, Location
from npc_manager import NpcManager
from health_manager import HealthManager
from death_manager import DeathManager
from char.sorceress import LightSorc, BlizzSorc, NovaSorc
from char.trapsin import Trapsin
from char.hammerdin import Hammerdin
from char.barbarian import Barbarian
from char.necro import Necro
from char.basic import Basic
from char.basic_ranged import Basic_Ranged

from run import Pindle, ShenkEld, Trav, Nihlatak, Arcane, Diablo
from town import TownManager, A1, A2, A3, A4, A5

# Added for dclone ip hunt
from messenger import Messenger
from utils.dclone_ip import get_d2r_game_ip

class Bot:
    def __init__(self, screen: Screen, game_stats: GameStats, template_finder: TemplateFinder, pick_corpse: bool = False):
        self._screen = screen
        self._game_stats = game_stats
        self._messenger = Messenger()
        self._config = Config()
        self._template_finder = template_finder
        self._item_finder = ItemFinder()
        self._ui_manager = UiManager(self._screen, self._template_finder)
        self._inventory_manager = InventoryManager(self._screen, self._template_finder, self._game_stats)
        self._belt_manager = BeltManager(self._screen, self._template_finder)
        self._pather = Pather(self._screen, self._template_finder)
        self._pickit = PickIt(self._screen, self._item_finder, self._ui_manager, self._belt_manager)

        # Create Character
        if self._config.char["type"] in ["sorceress", "light_sorc"]:
            self._char: IChar = LightSorc(self._config.light_sorc, self._screen, self._template_finder, self._ui_manager, self._pather)
        elif self._config.char["type"] == "blizz_sorc":
            self._char: IChar = BlizzSorc(self._config.blizz_sorc, self._screen, self._template_finder, self._ui_manager, self._pather)
        elif self._config.char["type"] == "nova_sorc":
            self._char: IChar = NovaSorc(self._config.nova_sorc, self._screen, self._template_finder, self._ui_manager, self._pather)
        elif self._config.char["type"] == "hammerdin":
            self._char: IChar = Hammerdin(self._config.hammerdin, self._screen, self._template_finder, self._ui_manager, self._pather)
        elif self._config.char["type"] == "trapsin":
            self._char: IChar = Trapsin(self._config.trapsin, self._screen, self._template_finder, self._ui_manager, self._pather)
        elif self._config.char["type"] == "barbarian":
            self._char: IChar = Barbarian(self._config.barbarian, self._screen, self._template_finder, self._ui_manager, self._pather)
        elif self._config.char["type"] == "necro":
            self._char: IChar = Necro(self._config.necro, self._screen, self._template_finder, self._ui_manager, self._pather)
        elif self._config.char["type"] == "basic":
            self._char: IChar = Basic(self._config.basic, self._screen, self._template_finder, self._ui_manager, self._pather)
        elif self._config.char["type"] == "basic_ranged":
            self._char: IChar = Basic_Ranged(self._config.basic_ranged, self._screen, self._template_finder, self._ui_manager, self._pather)
        else:
            Logger.error(f'{self._config.char["type"]} is not supported! Closing down bot.')
            os._exit(1)

        # Create Town Manager
        npc_manager = NpcManager(screen, self._template_finder)
        a5 = A5(self._screen, self._template_finder, self._pather, self._char, npc_manager)
        a4 = A4(self._screen, self._template_finder, self._pather, self._char, npc_manager)
        a3 = A3(self._screen, self._template_finder, self._pather, self._char, npc_manager)
        a2 = A2(self._screen, self._template_finder, self._pather, self._char, npc_manager)
        a1 = A1(self._screen, self._template_finder, self._pather, self._char, npc_manager)
        self._town_manager = TownManager(self._template_finder, self._ui_manager, self._inventory_manager, self._item_finder, a1, a2, a3, a4, a5)
        self._route_config = self._config.routes
        self._route_order = self._config.routes_order

        # Create runs
        if self._route_config["run_shenk"] and not self._route_config["run_eldritch"]:
            Logger.error("Running shenk without eldtritch is not supported. Either run none or both")
            os._exit(1)
        self._do_runs = {
            "run_trav": self._route_config["run_trav"],
            "run_pindle": self._route_config["run_pindle"],
            "run_shenk": self._route_config["run_shenk"] or self._route_config["run_eldritch"],
            "run_nihlathak": self._route_config["run_nihlathak"],
            "run_arcane": self._route_config["run_arcane"],
            "run_diablo": self._route_config["run_diablo"],
        }
        # Adapt order to the config
        self._do_runs = OrderedDict((k, self._do_runs[k]) for k in self._route_order if k in self._do_runs and self._do_runs[k])
        self._do_runs_reset = copy(self._do_runs)
        Logger.info(f"Doing runs: {self._do_runs_reset.keys()}")
        if self._config.general["randomize_runs"]:
            self.shuffle_runs()
        self._pindle = Pindle(self._template_finder, self._pather, self._town_manager, self._ui_manager, self._char, self._pickit)
        self._shenk = ShenkEld(self._template_finder, self._pather, self._town_manager, self._ui_manager, self._char, self._pickit)
        self._trav = Trav(self._template_finder, self._pather, self._town_manager, self._ui_manager, self._char, self._pickit)
        self._nihlatak = Nihlatak(self._screen, self._template_finder, self._pather, self._town_manager, self._ui_manager, self._char, self._pickit)
        self._arcane = Arcane(self._screen, self._template_finder, self._pather, self._town_manager, self._ui_manager, self._char, self._pickit)
        self._diablo = Diablo(self._screen, self._template_finder, self._pather, self._town_manager, self._ui_manager, self._char, self._pickit)

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
        self._states=['hero_selection', 'town', 'pindle', 'shenk', 'trav', 'nihlatak', 'arcane', 'diablo']
        self._transitions = [
            { 'trigger': 'create_game', 'source': 'hero_selection', 'dest': 'town', 'before': "on_create_game"},
            # Tasks within town
            { 'trigger': 'maintenance', 'source': 'town', 'dest': 'town', 'before': "on_maintenance"},
            # Different runs
            { 'trigger': 'run_pindle', 'source': 'town', 'dest': 'pindle', 'before': "on_run_pindle"},
            { 'trigger': 'run_shenk', 'source': 'town', 'dest': 'shenk', 'before': "on_run_shenk"},
            { 'trigger': 'run_trav', 'source': 'town', 'dest': 'trav', 'before': "on_run_trav"},
            { 'trigger': 'run_nihlathak', 'source': 'town', 'dest': 'nihlatak', 'before': "on_run_nihlathak"},
            { 'trigger': 'run_arcane', 'source': 'town', 'dest': 'arcane', 'before': "on_run_arcane"},
            { 'trigger': 'run_diablo', 'source': 'town', 'dest': 'nihlatak', 'before': "on_run_diablo"},
            # End run / game
            { 'trigger': 'end_run', 'source': ['shenk', 'pindle', 'nihlatak', 'trav', 'arcane', 'diablo'], 'dest': 'town', 'before': "on_end_run"},
            { 'trigger': 'end_game', 'source': ['town', 'shenk', 'pindle', 'nihlatak', 'trav', 'arcane', 'diablo','end_run'], 'dest': 'hero_selection', 'before': "on_end_game"},
        ]
        self.machine = Machine(model=self, states=self._states, initial="hero_selection", transitions=self._transitions, queued=True)

    def draw_graph(self):
        # Draw the whole graph, graphviz binaries must be installed and added to path for this!
        from transitions.extensions import GraphMachine
        self.machine = GraphMachine(model=self, states=self._states, initial="hero_selection", transitions=self._transitions, queued=True)
        self.machine.get_graph().draw('my_state_diagram.png', prog='dot')

    def get_belt_manager(self) -> BeltManager:
        return self._belt_manager

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
        self._do_runs = OrderedDict(tmp)

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
        self._template_finder.search_and_wait(["MAIN_MENU_TOP_LEFT","MAIN_MENU_TOP_LEFT_DARK"], roi=self._config.ui_roi["main_menu_top_left"])
        if not self._ui_manager.start_game(): return
        self._curr_loc = self._town_manager.wait_for_town_spawn()

        # Check for the current game ip and pause if we are able to obtain the hot ip
        if self._config.dclone["region_ips"] != "" and self._config.dclone["dclone_hotip"] != "":
            cur_game_ip = get_d2r_game_ip()
            hot_ip = self._config.dclone["dclone_hotip"]
            Logger.debug(f"Current Game IP: {cur_game_ip}   and HOTIP: {hot_ip}")
            if hot_ip == cur_game_ip:
                self._messenger.send_message(f"Dclone IP Found on IP: {cur_game_ip}")
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
            time.sleep(1.6)
            DeathManager.pick_up_corpse(self._screen)
            wait(1.2, 1.5)
            self._belt_manager.fill_up_belt_from_inventory(self._config.char["num_loot_columns"])
            wait(0.5)
        # Look at belt to figure out how many pots need to be picked up
        self._belt_manager.update_pot_needs()

        # Check inventory
        items = None
        if self._picked_up_items or self._no_stash_counter % 4 == 0:
            if self._no_stash_counter % 4 == 0:
                img=self._screen.grab()
                Logger.debug(f"tp: {self._inventory_manager.get_consumible_quantity(img, 'tp')}")
                Logger.debug(f"id: {self._inventory_manager.get_consumible_quantity(img, 'id')}")
                Logger.debug(f"keys: {self._inventory_manager.get_consumible_quantity(img, 'key')}")
                self._ui_manager.center_mouse()
            if self._inventory_manager._inventory_has_items():
                items = self._inventory_manager._inspect_items(item_finder=self._item_finder)
            else:
                self._inventory_manager.toggle_inventory("close")
        self._no_stash_counter += 1
        if items:
            # if there are still items that need identifying, identify them
            if any([item.need_id for item in items]):
                Logger.info("ID items at cain")
                self._curr_loc = self._town_manager.identify(self._curr_loc)
                keyboard.send("esc")
                wait(0.4, 0.6)
                if not self._curr_loc:
                    return self.trigger_or_stop("end_game", failed=True)
                # recheck inventory
                items = self._inventory_manager._inspect_items(item_finder=self._item_finder)

        # Stash stuff
        if items and any([item.keep for item in items]):
            Logger.info("Stashing items")
            self._curr_loc, result_items = self._town_manager.stash(self._curr_loc, items)
            if result_items: items = result_items
            if not self._curr_loc:
                return self.trigger_or_stop("end_game", failed=True)
            self._picked_up_items = False
            wait(1.0)
        sell_items = any([item.sell for item in items]) if items else None

        # Check if merc needs to be revived
        merc_alive = self._template_finder.search(["MERC_A2","MERC_A1","MERC_A5","MERC_A3"], self._screen.grab(), threshold=0.9, roi=self._config.ui_roi["merc_icon"]).valid
        if not merc_alive and self._config.char["use_merc"]:
            Logger.info("Resurrect merc")
            self._game_stats.log_merc_death()
            self._curr_loc = self._town_manager.resurrect(self._curr_loc)
            if not self._curr_loc:
                return self.trigger_or_stop("end_game", failed=True)

        # Check if should need some healing
        img = self._screen.grab()
        buy_pots = self._belt_manager.should_buy_pots()
        if HealthManager.get_health(img) < 0.6 or HealthManager.get_mana(img) < 0.2 or buy_pots:
            if buy_pots or sell_items:
                Logger.info("Buy pots at next possible Vendor")
                pot_needs = self._belt_manager.get_pot_needs()
                self._curr_loc, result_items = self._town_manager.buy_pots(self._curr_loc, pot_needs["health"], pot_needs["mana"], items)
                if result_items:
                    items = result_items
                    sell_items = any([item.sell for item in items]) if items else None
                wait(0.5, 0.8)
                self._belt_manager.update_pot_needs()
                # TODO: Remove this, currently workaround cause too lazy to add all the pathes from MALAH
                if self._curr_loc == Location.A5_MALAH:
                    if self._pather.traverse_nodes((Location.A5_MALAH, Location.A5_TOWN_START), self._char, force_move=True):
                        self._curr_loc = Location.A5_TOWN_START
                    else:
                        self._curr_loc = False
            else:
                Logger.info("Healing at next possible Vendor")
                self._curr_loc = self._town_manager.heal(self._curr_loc)
            if not self._curr_loc:
                return self.trigger_or_stop("end_game", failed=True)

        # Check if we are out of tps or need repairing
        need_repair = self._ui_manager.repair_needed()
        if self._tps_left < random.randint(3, 5) or need_repair or self._config.char["always_repair"] or sell_items:
            if need_repair: Logger.info("Repair needed. Gear is about to break")
            elif sell_items: Logger.info("Selling items")
            else: Logger.info("Repairing and exchanging tomes at next Vendor")
            self._curr_loc, result_items = self._town_manager.repair_and_fill_tomes(self._curr_loc, items)
            if result_items: items = result_items
            if not self._curr_loc:
                return self.trigger_or_stop("end_game", failed=True)
            self._tps_left = 20
            wait(1.0)

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
        if self._config.general["info_screenshots"] and failed:
            cv2.imwrite("./info_screenshots/info_failed_game_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        self._curr_loc = False
        self._pre_buffed = False
        self._ui_manager.save_and_exit()
        self._game_stats.log_end_game(failed=failed)
        self._do_runs = copy(self._do_runs_reset)
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
            if failed_run:
                self._no_stash_counter = 0 # this will force a check if we should stash on next game
            self.trigger_or_stop("end_game", failed=failed_run)
        else:
            self.trigger_or_stop("end_run")

    def on_run_pindle(self):
        res = False
        self._do_runs["run_pindle"] = False
        self._game_stats.update_location("Pin" if self._config.general['discord_status_condensed'] else "Pindle")
        self._curr_loc = self._pindle.approach(self._curr_loc)
        if self._curr_loc:
            res = self._pindle.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_shenk(self):
        res = False
        self._do_runs["run_shenk"] = False
        self._curr_loc = self._shenk.approach(self._curr_loc)
        if self._curr_loc:
            res = self._shenk.battle(self._route_config["run_shenk"], not self._pre_buffed, self._game_stats)
        self._ending_run_helper(res)

    def on_run_trav(self):
        res = False
        self._do_runs["run_trav"] = False
        self._game_stats.update_location("Trav" if self._config.general['discord_status_condensed'] else "Travincal")
        self._curr_loc = self._trav.approach(self._curr_loc)
        if self._curr_loc:
            res = self._trav.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_nihlathak(self):
        res = False
        self._do_runs["run_nihlathak"] = False
        self._game_stats.update_location("Nihl" if self._config.general['discord_status_condensed'] else "Nihlatak")
        self._curr_loc = self._nihlatak.approach(self._curr_loc)
        if self._curr_loc:
            res = self._nihlatak.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_arcane(self):
        res = False
        self._do_runs["run_arcane"] = False
        self._game_stats.update_location("Arc" if self._config.general['discord_status_condensed'] else "Arcane")
        self._curr_loc = self._arcane.approach(self._curr_loc)
        if self._curr_loc:
            res = self._arcane.battle(not self._pre_buffed)
        self._tps_left -= self._arcane.used_tps
        self._ending_run_helper(res)

    def on_run_diablo(self):
        res = False
        self._do_runs["run_diablo"] = False
        self._game_stats.update_location("Dia" if self._config.general['discord_status_condensed'] else "Diablo")
        self._curr_loc = self._diablo.approach(self._curr_loc)
        if self._curr_loc:
            res = self._diablo.battle(not self._pre_buffed)
        self._tps_left -= 1 # we use one tp at pentagram for calibration
        self._ending_run_helper(res)
