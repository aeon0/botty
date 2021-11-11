from transitions import Machine
import time
from char.hammerdin import Hammerdin
from template_finder import TemplateFinder
from item_finder import ItemFinder
from screen import Screen
from ui_manager import UiManager
from pather import Pather, Location
from logger import Logger
from char.sorceress import Sorceress
from char.i_char import IChar
from config import Config
from health_manager import HealthManager
from death_manager import DeathManager
from npc_manager import NpcManager, Npc
from pickit import PickIt
from utils.misc import wait, send_discord
import keyboard
import threading
import time
import os
import random


class Bot:
    def __init__(self):
        self._config = Config()
        self._screen = Screen(self._config.general["monitor"])
        self._template_finder = TemplateFinder(self._screen)
        self._item_finder = ItemFinder()
        self._ui_manager = UiManager(self._screen, self._template_finder)
        self._pather = Pather(self._screen, self._template_finder)
        self._health_manager = HealthManager(self._screen, self._template_finder, self._ui_manager)
        self._death_manager = DeathManager(self._screen, self._template_finder)
        self._npc_manager = NpcManager(self._screen, self._template_finder)
        self._pickit = PickIt(self._screen, self._item_finder, self._ui_manager)
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
        self._timer = None
        self._tps_left = 20

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

    def start(self):
        self.trigger('create_game')

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
        if self._timer is not None:
            delay = self._config.general["min_game_length_s"] - (time.time() - self._timer)
            if delay > 0.5:
                Logger.info(f"Delay game creation for {delay:.2f} s")
                wait(delay, delay + 5.0)
        Logger.info("Start new game")
        self._timer = time.time()
        found, _ = self._template_finder.search_and_wait("D2_LOGO_HS", time_out=70)
        if not found:
            Logger.error("Something went wrong here, bot is unsure about current location. Closing down bot.")
            if self._config.general["custom_discord_hook"] != "":
                send_discord_thread = threading.Thread(target=send_discord, args=("Botty got stuck and can not resume", self._config.general["custom_discord_hook"]))
                send_discord_thread.daemon = True
                send_discord_thread.start()
            self._ui_manager.save_and_exit()
            os._exit(1)
        self._ui_manager.start_game()
        self._template_finder.search_and_wait("A5_TOWN_1")
        self._tp_is_up = False
        self._curr_location = Location.A5_TOWN_START
        # Make sure these keys are released
        keyboard.release(self._config.char["stand_still"])
        keyboard.release(self._config.char["show_items"])
        self.trigger("maintenance")

    def on_maintenance(self):
        time.sleep(0.6)

        if self._death_manager.died() or self._health_manager.did_chicken():
            # Also do this for did_chicken because we can not be 100% sure that chicken did not press esc before
            # the death manager could determine if we were dead
            self._death_manager.pick_up_corpse()
            # TODO: maybe it is time for a special BeltManager?
            wait(1.2, 1.5)
            self._ui_manager.fill_up_belt_from_inventory(self._config.char["num_loot_columns"])

        # Check if healing is needed, TODO: add shoping e.g. for potions
        img = self._screen.grab()
        # TODO: If tp is up we always go back into the portal...
        if not self._tp_is_up and (self._health_manager.get_health(img) < 0.6 or self._health_manager.get_mana(img) < 0.3):
            Logger.info("Need some healing first. Go talk to Malah")
            if not self._pather.traverse_nodes(self._curr_location, Location.MALAH, self._char): 
                self.trigger("end_game")
                return
            self._curr_location = Location.MALAH
            self._npc_manager.open_npc_menu(Npc.MALAH)
            if not self._pather.traverse_nodes(self._curr_location, Location.A5_TOWN_START, self._char):
                self.trigger("end_game")
                return
            self._curr_location = Location.A5_TOWN_START

        # Stash stuff
        if self._picked_up_items:
            Logger.info("Stashing picked up items")
            if not self._pather.traverse_nodes(self._curr_location, Location.A5_STASH, self._char):
                self.trigger("end_game")
                return
            self._curr_location = Location.A5_STASH
            time.sleep(1.5)
            # sometimes waypoint is opened and stash not found because of that, check for that
            if self._template_finder.search("WAYPOINT_MENU", self._screen.grab())[0]:
                keyboard.send("esc")
            if self._char.select_by_template("A5_STASH"):
                self._ui_manager.stash_all_items(self._config.char["num_loot_columns"])
                self._picked_up_items = False
                time.sleep(2) # otherwise next grab of screen will still have inventory
            else:
                Logger.warning("Could not find stash, continue...")

        if self._tps_left < 4:
            Logger.info("Repairing and buying tps at Lazurk")
            if not self._pather.traverse_nodes(self._curr_location, Location.LARZUK, self._char):
                self.trigger("end_game")
                return
            self._curr_location = Location.LARZUK
            self._npc_manager.open_npc_menu(Npc.LARZUK)
            self._npc_manager.press_npc_btn(Npc.LARZUK, "trade_repair")
            if self._ui_manager.repair_and_fill_up_tp(close_when_done=True):
                self._tps_left = 20
            wait(0.8)

        # Check if merc needs to be revived
        merc_alive, _ = self._template_finder.search("MERC", self._screen.grab(), threshold=0.9, roi=[0, 0, 200, 200])
        if not merc_alive:
            Logger.info("Reviveing merc")
            if not self._pather.traverse_nodes(self._curr_location, Location.QUAL_KEHK, self._char):
                self.trigger("end_game")
                return
            self._curr_location = Location.QUAL_KEHK
            if self._npc_manager.open_npc_menu(Npc.QUAL_KEHK):
                self._npc_manager.press_npc_btn(Npc.QUAL_KEHK, "resurrect")
            time.sleep(2)

        # Start a new run
        started_run = False
        for key in self._do_runs:
            if self._do_runs[key]:
                self.trigger(key)
                started_run = True
                break
        if not started_run:
            self.trigger("end_game")

    def _start_run(self, key, run):
        Logger.info(f"{key}")
        self._do_runs[key] = False
        run_thread = threading.Thread(target=run.doit, args=(self,))
        run_thread.start()
        # Set up monitoring
        health_monitor_thread = threading.Thread(target=self._health_manager.start_monitor, args=(run_thread,))
        health_monitor_thread.start()
        death_monitor_thread = threading.Thread(target=self._death_manager.start_monitor, args=(run_thread,))
        death_monitor_thread.start()
        run_thread.join()
        # Run done, lets stop health monitoring and death monitoring
        self._health_manager.stop_monitor()
        health_monitor_thread.join()
        if self._health_manager.did_chicken():
            # in case of chicken give the death manager some time to pick up on possible death flag
            # since death monitor does not check with the same frequency to save on runtime
            wait(self._death_manager.get_loop_delay() + 1.0)
        self._death_manager.stop_monitor()
        death_monitor_thread.join()

        if self._death_manager.died() or self._health_manager.did_chicken() or self.is_last_run() or not run.success:
            self.trigger("end_game")
        else:
            self.trigger("end_run")

    def on_run_pindle(self):
        class RunPindle:
            def __init__(self):
                self.success = False
            def doit(self, bot: Bot):
                self.success = bot._pather.traverse_nodes(bot._curr_location, Location.NIHLATHAK_PORTAL, bot._char)
                if not self.success:
                    return
                bot._curr_location = Location.NIHLATHAK_PORTAL
                wait(0.2, 0.4)
                self.success &= bot._char.select_by_template("A5_RED_PORTAL")
                self.success &= bot._template_finder.search_and_wait("PINDLE_0", time_out=20)[0]
                if not self.success:
                    return
                bot._char.pre_buff()
                wait(0.2, 0.3)
                if bot._config.char["static_path_pindle"]:
                    bot._pather.traverse_nodes_fixed("PINDLE_SAVE_DIST", bot._char)
                else:
                    bot._pather.traverse_nodes(Location.PINDLE_START, Location.PINDLE_SAVE_DIST, bot._char)
                bot._char.kill_pindle()
                wait(1.5, 1.8)
                bot._picked_up_items = bot._pickit.pick_up_items(bot._char)
                # in order to move away for items to have a clear tp, move to the end of the hall
                if not bot.is_last_run():
                    bot._pather.traverse_nodes_fixed("PINDLE_SAVE_TP", bot._char)
                wait(0.2, 0.3)
                self.success = True
                return
        run = RunPindle()
        self._start_run("run_pindle", run)

    def on_run_shenk(self):
        class RunShenk:
            def __init__(self):
                self.success = False
            def doit(self, bot: Bot):
                self.success = bot._pather.traverse_nodes(bot._curr_location, Location.A5_WP, bot._char)
                if not self.success:
                    return
                bot._curr_location = Location.A5_WP
                wait(0.6)
                bot._char.select_by_template("A5_WP")
                wait(1.0)
                bot._ui_manager.use_wp(4, 1)
                self.success = bot._template_finder.search_and_wait("ELDRITCH_0", time_out=20)[0]
                if not self.success:
                    return
                bot._char.pre_buff()
                wait(0.2, 0.3)
                # eldritch
                if bot._config.char["static_path_eldritch"]:
                    bot._pather.traverse_nodes_fixed("ELDRITCH_SAVE_DIST", bot._char)
                else:
                    bot._pather.traverse_nodes(Location.ELDRITCH_START, Location.ELDRITCH_SAVE_DIST, bot._char)
                bot._char.kill_eldritch()
                wait(0.4)
                bot._picked_up_items = bot._pickit.pick_up_items(bot._char)
                if not bot.is_last_run() and not bot._route_config["run_shenk"]:
                    bot._pather.traverse_nodes_fixed("ELDRITCH_SAVE_TP", bot._char)
                # shenk
                if bot._route_config["run_shenk"]:
                    self.success = bot._pather.traverse_nodes(Location.SHENK_START, Location.SHENK_SAVE_DIST, bot._char)
                    if not self.success:
                        return
                    wait(0.15, 0.2)
                    bot._char.kill_shenk()
                    wait(0.5)
                    # do two pickups on shenk because flames sometimes mess up item search
                    bot._picked_up_items |= bot._pickit.pick_up_items(bot._char)
                    wait(1.5, 1.8)
                    bot._picked_up_items |= bot._pickit.pick_up_items(bot._char)
                    # in order to move away for items to have a clear tp, move to the end of the hall
                    if not bot.is_last_run():
                        bot._pather.traverse_nodes_fixed("SHENK_SAVE_TP", bot._char)
                wait(0.5, 0.6)
                self.success = True
                return
        run = RunShenk()
        self._start_run("run_shenk", run)

    def on_end_game(self):
        if self._health_manager.did_chicken() or self._death_manager.died():
            # This is a tricky state as we send different actions in different threads.
            # Chicken could have been succesfull which means we are at hero selection screen
            # Chicken could have been unsuccesfull, which means we are naked in a5_town
            time.sleep(3) # just to take our time here
            is_loading = True
            while is_loading:
                is_loading = self._template_finder.search("LOADING", self._screen.grab())[0]
                time.sleep(0.5)
            # Okay we are sure we are not in loading screen, let's check if we are in hero selection or in a5 town
            img = self._screen.grab()
            if self._template_finder.search("A5_TOWN_1", img)[0]:
                self._ui_manager.save_and_exit()
            elif self._template_finder.search("D2_LOGO_HS", img)[0]:
                pass # no need to do anything
            else:
                Logger.error("Could not determine location after chicken / death. Can not continue...")
                os._exit(1)
        else:
            self._ui_manager.save_and_exit()

        if self._timer is not None:
            elapsed_time = time.time() - self._timer
            Logger.info(f"End game. Elapsed time: {elapsed_time:.2f}s")
        self._do_runs = {
            "run_pindle": self._route_config["run_pindle"],
            "run_shenk": self._route_config["run_shenk"] or self._route_config["run_eldritch"]
        }
        if self._config.general["randomize_runs"]:
            self.shuffle_runs()
        wait(0.2, 0.5)
        self.trigger("create_game")

    def on_end_run(self):
        success = self._char.tp_town()
        self._tps_left -= 1
        if success:
            success, _= self._template_finder.search_and_wait("A5_TOWN_1", time_out=10)
            if success:
                self._tp_is_up = True
                self._curr_location = Location.A5_TOWN_START
                self.trigger("maintenance")
            else:
                self.trigger("end_game")
        else:
            self.trigger("end_game")


if __name__ == "__main__":
    import keyboard
    keyboard.add_hotkey("f12", lambda: os._exit(1))
    keyboard.wait("f11")
    bot = Bot()
    bot.state = "a5_town"
    bot._curr_location = Location.A5_TOWN_START
    bot.on_maintenance()
