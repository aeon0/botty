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
from transmute import Transmute

from utils.misc import wait
from game_stats import GameStats
from logger import Logger
from config import Config
from screen import grab
from template_finder import TemplateFinder
from char import IChar
from item import ItemFinder
from item.pickit import PickIt
from pather import Pather, Location
from death_manager import DeathManager
from char.sorceress import LightSorc, BlizzSorc, NovaSorc
from char.trapsin import Trapsin
from char.hammerdin import Hammerdin
from char.barbarian import Barbarian
from char.necro import Necro
from char.basic import Basic
from char.basic_ranged import Basic_Ranged
from ui_manager import wait_for_screen_object, detect_screen_object, ScreenObjects
from ui import meters, skills, view, character_select, main_menu
from inventory import personal, vendor, stash, belt, common, consumables

from run import Pindle, ShenkEld, Trav, Nihlathak, Arcane, Diablo
from town import TownManager, A1, A2, A3, A4, A5, town_manager

# Added for dclone ip hunt
from messages import Messenger
from utils.dclone_ip import get_d2r_game_ip

class Bot:
    _MAIN_MENU_MARKERS = ["MAIN_MENU_TOP_LEFT","MAIN_MENU_TOP_LEFT_DARK"]

    def __init__(self, game_stats: GameStats):
        self._game_stats = game_stats
        self._messenger = Messenger()
        self._item_finder = ItemFinder()
        self._pather = Pather()
        self._pickit = PickIt(self._item_finder)

        # Create Character
        if Config().char["type"] in ["sorceress", "light_sorc"]:
            self._char: IChar = LightSorc(Config().light_sorc, self._pather)
        elif Config().char["type"] == "blizz_sorc":
            self._char: IChar = BlizzSorc(Config().blizz_sorc, self._pather)
        elif Config().char["type"] == "nova_sorc":
            self._char: IChar = NovaSorc(Config().nova_sorc, self._pather)
        elif Config().char["type"] == "hammerdin":
            self._char: IChar = Hammerdin(Config().hammerdin, self._pather, self._pickit) #pickit added for diablo
        elif Config().char["type"] == "trapsin":
            self._char: IChar = Trapsin(Config().trapsin, self._pather)
        elif Config().char["type"] == "barbarian":
            self._char: IChar = Barbarian(Config().barbarian, self._pather)
        elif Config().char["type"] == "necro":
            self._char: IChar = Necro(Config().necro, self._pather)
        elif Config().char["type"] == "basic":
            self._char: IChar = Basic(Config().basic, self._pather)
        elif Config().char["type"] == "basic_ranged":
            self._char: IChar = Basic_Ranged(Config().basic_ranged, self._pather)
        else:
            Logger.error(f'{Config().char["type"]} is not supported! Closing down bot.')
            os._exit(1)

        # Create Town Manager
        a5 = A5(self._pather, self._char)
        a4 = A4(self._pather, self._char)
        a3 = A3(self._pather, self._char)
        a2 = A2(self._pather, self._char)
        a1 = A1(self._pather, self._char)
        self._town_manager = TownManager(a1, a2, a3, a4, a5)

        # Create runs
        if Config().routes["run_shenk"] and not Config().routes["run_eldritch"]:
            Logger.error("Running shenk without eldtritch is not supported. Either run none or both")
            os._exit(1)
        self._do_runs = {
            "run_trav": Config().routes["run_trav"],
            "run_pindle": Config().routes["run_pindle"],
            "run_shenk": Config().routes["run_shenk"] or Config().routes["run_eldritch"],
            "run_nihlathak": Config().routes["run_nihlathak"],
            "run_arcane": Config().routes["run_arcane"],
            "run_diablo": Config().routes["run_diablo"],
        }
        # Adapt order to the config
        self._do_runs = OrderedDict((k, self._do_runs[k]) for k in Config().routes_order if k in self._do_runs and self._do_runs[k])
        self._do_runs_reset = copy(self._do_runs)
        Logger.info(f"Doing runs: {self._do_runs_reset.keys()}")
        if Config().general["randomize_runs"]:
            self.shuffle_runs()
        self._pindle = Pindle(self._pather, self._town_manager, self._char, self._pickit)
        self._shenk = ShenkEld(self._pather, self._town_manager, self._char, self._pickit)
        self._trav = Trav(self._pather, self._town_manager, self._char, self._pickit)
        self._nihlathak = Nihlathak(self._pather, self._town_manager, self._char, self._pickit)
        self._arcane = Arcane(self._pather, self._town_manager, self._char, self._pickit)
        self._diablo = Diablo(self._pather, self._town_manager, self._char, self._pickit)

        # Create member variables
        self._pick_corpse = False
        self._picked_up_items = False
        self._curr_loc: Union[bool, Location] = None
        self._use_id_tome = True
        self._use_keys = True
        self._pre_buffed = False
        self._stopping = False
        self._pausing = False
        self._current_threads = []
        self._ran_no_pickup = False
        self._previous_run_failed = False

        # Create State Machine
        self._states=['initialization','hero_selection', 'town', 'pindle', 'shenk', 'trav', 'nihlathak', 'arcane', 'diablo']
        self._transitions = [
            { 'trigger': 'init', 'source': 'initialization', 'dest': '=','before': "on_init"},
            { 'trigger': 'select_character', 'source': 'initialization', 'dest': 'hero_selection', 'before': "on_select_character"},
            { 'trigger': 'start_from_town', 'source': ['initialization', 'hero_selection'], 'dest': 'town', 'before': "on_start_from_town"},
            { 'trigger': 'create_game', 'source': 'hero_selection', 'dest': '=', 'before': "on_create_game"},
            # Tasks within town
            { 'trigger': 'maintenance', 'source': 'town', 'dest': 'town', 'before': "on_maintenance"},
            # Different runs
            { 'trigger': 'run_pindle', 'source': 'town', 'dest': 'pindle', 'before': "on_run_pindle"},
            { 'trigger': 'run_shenk', 'source': 'town', 'dest': 'shenk', 'before': "on_run_shenk"},
            { 'trigger': 'run_trav', 'source': 'town', 'dest': 'trav', 'before': "on_run_trav"},
            { 'trigger': 'run_nihlathak', 'source': 'town', 'dest': 'nihlathak', 'before': "on_run_nihlathak"},
            { 'trigger': 'run_arcane', 'source': 'town', 'dest': 'arcane', 'before': "on_run_arcane"},
            { 'trigger': 'run_diablo', 'source': 'town', 'dest': 'nihlathak', 'before': "on_run_diablo"},
            # End run / game
            { 'trigger': 'end_run', 'source': ['shenk', 'pindle', 'nihlathak', 'trav', 'arcane', 'diablo'], 'dest': 'town', 'before': "on_end_run"},
            { 'trigger': 'end_game', 'source': ['town', 'shenk', 'pindle', 'nihlathak', 'trav', 'arcane', 'diablo','end_run'], 'dest': 'initialization', 'before': "on_end_game"},
        ]
        self.machine = Machine(model=self, states=self._states, initial="initialization", transitions=self._transitions, queued=True)
        self._transmute = Transmute(self._game_stats)


    def draw_graph(self):
        # Draw the whole graph, graphviz binaries must be installed and added to path for this!
        from transitions.extensions import GraphMachine
        self.machine = GraphMachine(model=self, states=self._states, initial="initialization", transitions=self._transitions, queued=True)
        self.machine.get_graph().draw('my_state_diagram.png', prog='dot')

    def get_curr_location(self):
        return self._curr_loc

    def start(self):
        self.trigger_or_stop('init')

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
            Logger.info(f"{Config().general['name']} is now pausing")
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

    def _rebuild_as_asset_to_trigger(trigger_to_assets: dict):
        result = {}
        for key in trigger_to_assets.keys():
            for asset in trigger_to_assets[key]:
                result[asset] = key
        return result

    def on_init(self):
        self._game_stats.log_start_game()
        keyboard.release(Config().char["stand_still"])
        transition_to_screens = Bot._rebuild_as_asset_to_trigger({
            "select_character": Bot._MAIN_MENU_MARKERS,
            "start_from_town": town_manager.TOWN_MARKERS,
        })
        match = TemplateFinder().search_and_wait(list(transition_to_screens.keys()), best_match=True)
        self.trigger_or_stop(transition_to_screens[match.name])

    def on_select_character(self):
        if Config().general['restart_d2r_when_stuck']:
            # Make sure the correct char is selected
            if character_select.has_char_template_saved():
                character_select.select_char()
            else:
                character_select.save_char_online_status()
                character_select.save_char_template()
        self.trigger_or_stop("create_game")

    def on_create_game(self):
        # Start a game from hero selection
        m = wait_for_screen_object(ScreenObjects.MainMenu)
        if m.valid:
            if "DARK" in m.name:
                keyboard.send("esc")
            main_menu.start_game()
            view.move_to_corpse()
        else: return
        self.trigger_or_stop("start_from_town")

    def on_start_from_town(self):
        self._curr_loc = self._town_manager.wait_for_town_spawn()
        # Check for the current game ip and pause if we are able to obtain the hot ip
        if Config().dclone["region_ips"] != "" and Config().dclone["dclone_hotip"] != "":
            cur_game_ip = get_d2r_game_ip()
            hot_ip = Config().dclone["dclone_hotip"]
            Logger.debug(f"Current Game IP: {cur_game_ip}   and HOTIP: {hot_ip}")
            if hot_ip == cur_game_ip:
                self._messenger.send_message(f"Dclone IP Found on IP: {cur_game_ip}")
                print("Press Enter")
                input()
                os._exit(1)
            else:
                Logger.info(f"Please Enter the region ip and hot ip on config to use")

        # Run /nopickup command to avoid picking up stuff on accident
        if not self._ran_no_pickup and not self._game_stats._nopickup_active:
            self._ran_no_pickup = True
            if view.enable_no_pickup():
                self._game_stats._nopickup_active = True
                Logger.info("Activated /nopickup")
            else:
                Logger.error("Failed to detect if /nopickup command was applied or not")
        self.trigger_or_stop("maintenance")

    def on_maintenance(self):
        # Handle picking up corpse in case of death
        self._pick_corpse = detect_screen_object(ScreenObjects.Corpse).valid
        if self._pick_corpse:
            self._previous_run_failed = True
            time.sleep(1.6)
            view.pickup_corpse()
            wait(1.2, 1.5)
            belt.fill_up_belt_from_inventory(Config().char["num_loot_columns"])
            wait(0.5)
        self._char.discover_capabilities()
        if self._pick_corpse and self._char.capabilities.can_teleport_with_charges and not self._char.select_tp():
            keybind = self._char._skill_hotkeys["teleport"]
            Logger.info(f"Teleport keybind is lost upon death. Rebinding teleport to '{keybind}'")
            self._char.remap_right_skill_hotkey("TELE_ACTIVE", self._char._skill_hotkeys["teleport"])

        # Look at belt to figure out how many pots need to be picked up
        belt.update_pot_needs()

        # Inspect inventory
        items = None

        need_inspect = self._picked_up_items or self._previous_run_failed
        if Config().char["runs_per_stash"]:
            need_inspect |= (self._game_stats._run_counter - 1) % Config().char["runs_per_stash"] == 0
        if need_inspect:
            img = personal.open()
            # Update TP, ID, key needs
            if self._game_stats._game_counter == 1:
                self._use_id_tome = common.tome_state(img, 'id')[0] is not None
                self._use_keys = detect_screen_object(ScreenObjects.Key, img).valid
            if (self._game_stats._run_counter - 1) % 4 == 0 or self._previous_run_failed:
                consumables.update_tome_key_needs(img, item_type = 'tp')
                if self._use_id_tome:
                    id_state = common.tome_state(img, 'id')[0]
                    if id_state == "empty":
                        consumables.set_needs("id", 20)
                    else:
                        consumables.update_tome_key_needs(img, item_type = 'id')
                if self._use_keys:
                    # if keys run out then refilling will be unreliable :(
                    self._use_keys = consumables.update_tome_key_needs(img, item_type = 'key')
            # Check inventory items
            if personal.inventory_has_items(img):
                Logger.debug("Inspecting inventory items")
                items = personal.inspect_items(img)
            else:
                common.close()
        Logger.debug(f"Needs: {consumables.get_needs()}")
        if items:
            # if there are still items that need identifying, go to cain to identify them
            if any([item.need_id for item in items]):
                Logger.info("ID items at cain")
                self._curr_loc = self._town_manager.identify(self._curr_loc)
                if not self._curr_loc:
                    return self.trigger_or_stop("end_game", failed=True)
                # recheck inventory
                items = personal.inspect_items()
        keep_items = any([item.keep for item in items]) if items else None
        sell_items = any([item.sell for item in items]) if items else None

        # Check if should need some healing
        img = grab()
        need_refill = (
            consumables.should_buy("health", min_needed = 3) or
            consumables.should_buy("mana", min_needed = 3) or
            (self._use_keys and consumables.should_buy("key", min_remaining = 4)) or
            consumables.should_buy("tp", min_remaining = 3) or
            consumables.should_buy("id", min_remaining = 3)
        )
        if need_refill:
            Logger.info("Buy pots/keys/scrolls at next possible Vendor")
            self._curr_loc, result_items = self._town_manager.buy_consumables(self._curr_loc, items = items, needs = consumables.get_needs())
            if self._curr_loc:
                items = result_items
                sell_items = any([item.sell for item in items]) if items else None
                for x in ["health", "mana", "key", "tp", "id"]:
                    consumables.set_needs(x, 0)
                Logger.debug(f"Needs: {consumables.get_needs()}")
            wait(0.5, 0.8)
        elif meters.get_health(img) < 0.6 or meters.get_mana(img) < 0.2:
            Logger.info("Healing at next possible Vendor")
            self._curr_loc = self._town_manager.heal(self._curr_loc)
        if not self._curr_loc:
            return self.trigger_or_stop("end_game", failed=True)

        # Stash stuff, either when item was picked up or after X runs without stashing because of unwanted loot in inventory
        if keep_items:
            if personal.should_stash():
                Logger.info("Stashing items")
                self._curr_loc, result_items = self._town_manager.stash(self._curr_loc, items=items)
                Logger.info("Running transmutes")
                self._transmute.run_transmutes(force=False)
                common.close()
                if not self._curr_loc:
                    return self.trigger_or_stop("end_game", failed=True)
                self._picked_up_items = False
                wait(1.0)

        # Check if we are out of tps or need repairing
        need_repair = detect_screen_object(ScreenObjects.NeedRepair).valid
        need_routine_repair = False if not Config().char["runs_per_repair"] else self._game_stats._run_counter % Config().char["runs_per_repair"] == 0
        need_refill_teleport = self._char.capabilities.can_teleport_with_charges and (not self._char.select_tp() or self._char.is_low_on_teleport_charges())
        if need_repair or need_routine_repair or need_refill_teleport or sell_items:
            if need_repair:
                Logger.info("Repair needed. Gear is about to break")
            elif need_routine_repair:
                Logger.info(f"Routine repair. Run count={self._game_stats._run_counter}, runs_per_repair={Config().char['runs_per_repair']}")
            elif need_refill_teleport:
                Logger.info("Teleport charges ran out. Need to repair")
            elif sell_items:
                Logger.info("Selling items at repair vendor")
            self._curr_loc, result_items = self._town_manager.repair(self._curr_loc, items)
            if self._curr_loc:
                items = result_items
            if not self._curr_loc:
                return self.trigger_or_stop("end_game", failed=True)
            wait(1.0)

        # Check if merc needs to be revived
        match = detect_screen_object(ScreenObjects.MercIcon)
        if not match.valid and Config().char["use_merc"]:
            Logger.info("Resurrect merc")
            self._game_stats.log_merc_death()
            self._curr_loc = self._town_manager.resurrect(self._curr_loc)
            if not self._curr_loc:
                return self.trigger_or_stop("end_game", failed=True)

        # Check if gambling is needed
        if stash.gambling_needed() and Config().char["gamble_items"]:
            for x in range (4):
                self._curr_loc = self._town_manager.gamble(self._curr_loc)
                vendor.gamble()
                items = None
                if personal.inventory_has_items(img):
                    items = personal.inspect_items(img)
                    common.close()
                    if (x ==3):
                        self._curr_loc, _ = self._town_manager.stash(self._curr_loc, items = items)
                    else:
                        self._curr_loc, _ = self._town_manager.stash(self._curr_loc, gamble=True, items = items)
                    if not self._curr_loc:
                        return self.trigger_or_stop("end_game", failed=True)
            stash.set_gold_full(False)

        # Start a new run
        started_run = False
        self._previous_run_failed = False
        for key in self._do_runs:
            if self._do_runs[key]:
                self.trigger_or_stop(key)
                started_run = True
                break
        if not started_run:
            self.trigger_or_stop("end_game")

    def on_end_game(self, failed: bool = False):
        if Config().general["info_screenshots"] and failed:
            cv2.imwrite("./info_screenshots/info_failed_game_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
        self._curr_loc = False
        self._pre_buffed = False
        view.save_and_exit()
        self._game_stats.log_end_game(failed=failed)
        self._do_runs = copy(self._do_runs_reset)
        if Config().general["randomize_runs"]:
            self.shuffle_runs()
        wait(0.2, 0.5)
        self.trigger_or_stop("init")

    def on_end_run(self):
        if not Config().char["pre_buff_every_run"]:
            self._pre_buffed = True
        success = self._char.tp_town()
        if success:
            self._curr_loc = self._town_manager.wait_for_tp(self._curr_loc)
            if self._curr_loc:
                return self.trigger_or_stop("maintenance")
        if not skills.has_tps():
            consumables.set_needs("tp", 20)
        self.trigger_or_stop("end_game", failed=True)

    # All the runs go here
    # ==================================
    def _ending_run_helper(self, res: Union[bool, tuple[Location, bool]]):
        self._game_stats._run_counter += 1
        # either fill member variables with result data or mark run as failed
        failed_run = True
        if res:
            failed_run = False
            self._curr_loc, self._picked_up_items = res
        # in case its the last run or the run was failed, end game, otherwise move to next run
        if self.is_last_run() or failed_run:
            if failed_run:
                self._previous_run_failed = True
            self.trigger_or_stop("end_game", failed=failed_run)
        else:
            self.trigger_or_stop("end_run")

    def on_run_pindle(self):
        res = False
        self._do_runs["run_pindle"] = False
        self._game_stats.update_location("Pin" if Config().general['discord_status_condensed'] else "Pindle")
        self._curr_loc = self._pindle.approach(self._curr_loc)
        if self._curr_loc:
            res = self._pindle.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_shenk(self):
        res = False
        self._do_runs["run_shenk"] = False
        self._curr_loc = self._shenk.approach(self._curr_loc)
        if self._curr_loc:
            res = self._shenk.battle(Config().routes["run_shenk"], not self._pre_buffed, self._game_stats)
        self._ending_run_helper(res)

    def on_run_trav(self):
        res = False
        self._do_runs["run_trav"] = False
        self._game_stats.update_location("Trav" if Config().general['discord_status_condensed'] else "Travincal")
        self._curr_loc = self._trav.approach(self._curr_loc)
        if self._curr_loc:
            res = self._trav.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_nihlathak(self):
        res = False
        self._do_runs["run_nihlathak"] = False
        self._game_stats.update_location("Nihl" if Config().general['discord_status_condensed'] else "Nihlathak")
        self._curr_loc = self._nihlathak.approach(self._curr_loc)
        if self._curr_loc:
            res = self._nihlathak.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_arcane(self):
        res = False
        self._do_runs["run_arcane"] = False
        self._game_stats.update_location("Arc" if Config().general['discord_status_condensed'] else "Arcane")
        self._curr_loc = self._arcane.approach(self._curr_loc)
        if self._curr_loc:
            res = self._arcane.battle(not self._pre_buffed)
        self._ending_run_helper(res)

    def on_run_diablo(self):
        res = False
        self._do_runs["run_diablo"] = False
        self._game_stats.update_location("Dia" if Config().general['discord_status_condensed'] else "Diablo")
        self._curr_loc = self._diablo.approach(self._curr_loc)
        if self._curr_loc:
            res = self._diablo.battle(not self._pre_buffed)
        self._ending_run_helper(res)
