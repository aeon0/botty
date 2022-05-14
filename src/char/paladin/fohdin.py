from asyncio.windows_events import NULL
from pickle import TRUE
import random
import keyboard
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab
from utils.custom_mouse import mouse
from char.paladin import Paladin
from logger import Logger
from config import Config
from utils.misc import wait, rotate_vec, unit_vector
import time
from pather import Location
import numpy as np

#import cv2 #for Diablo
#from item.pickit import PickIt #for Diablo
#import numpy as np
from target_detect import get_visible_targets, TargetInfo

class FoHdin(Paladin):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up FoHdin")
        super().__init__(*args, **kwargs)
        self._pather.adapt_path((Location.A3_TRAV_START, Location.A3_TRAV_CENTER_STAIRS), [220, 221, 222, 903, 904, 905, 906])

    def _cast_foh(self, cast_pos_abs: tuple[float, float], spray: int = 10, time_in_s: float = 1, aura: str = "conviction"):
        if aura in self._skill_hotkeys and self._skill_hotkeys[aura]:
            keyboard.send(self._skill_hotkeys[aura])
            wait(0.05, 0.1)
            keyboard.send(Config().char["stand_still"], do_release=False)
            wait(0.05, 0.1)
            if self._skill_hotkeys["foh"]:
                keyboard.send(self._skill_hotkeys["foh"])
            wait(0.05, 0.1)
            start = time.time()
            while (time.time() - start) < time_in_s:
                x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
                y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
                pos_m = convert_abs_to_monitor((x, y))
                mouse.move(*pos_m, delay_factor=[0.3, 0.6])
                wait(0.06, 0.08)
                mouse.press(button="left")
                wait(0.1, 0.2)
                mouse.release(button="left")
            wait(0.01, 0.05)
            keyboard.send(Config().char["stand_still"], do_press=False)

    def _cast_holy_bolt(self, cast_pos_abs: tuple[float, float], spray: int = 10, time_in_s: float = 4, aura: str = "conviction"):
        if aura in self._skill_hotkeys and self._skill_hotkeys[aura]:
            keyboard.send(self._skill_hotkeys[aura])
            wait(0.05, 0.1)
            keyboard.send(Config().char["stand_still"], do_release=False)
            wait(0.05, 0.1)
            if self._skill_hotkeys["holy_bolt"]:
                keyboard.send(self._skill_hotkeys["holy_bolt"])
            wait(0.05, 0.1)
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            pos_m = convert_abs_to_monitor((x, y))
            mouse.move(*pos_m, delay_factor=[0.3, 0.6])
            start = time.time()
            while (time.time() - start) < time_in_s:
                wait(0.06, 0.08)
                mouse.press(button="left")
                wait(0.1, 0.2)
                mouse.release(button="left")
            wait(0.01, 0.05)
            keyboard.send(Config().char["stand_still"], do_press=False)

    #for nihlathak
    def _cast_hammers(self, time_in_s: float, aura: str = "concentration"):
        if aura in self._skill_hotkeys and self._skill_hotkeys[aura]:
            keyboard.send(self._skill_hotkeys[aura])
            wait(0.05, 0.1)
            keyboard.send(Config().char["stand_still"], do_release=False)
            wait(0.05, 0.1)
            if self._skill_hotkeys["blessed_hammer"]:
                keyboard.send(self._skill_hotkeys["blessed_hammer"])
            wait(0.05, 0.1)
            start = time.time()
            while (time.time() - start) < time_in_s:
                wait(0.06, 0.08)
                mouse.press(button="left")
                wait(0.1, 0.2)
                mouse.release(button="left")
            wait(0.01, 0.05)
            keyboard.send(Config().char["stand_still"], do_press=False)

    #for nihalthak
    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float):
        pos_m = convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_hammers(atk_len)

    def kill_pindle(self) -> bool:
        if not Config().char['cs_mob_detect'] or get_visible_targets():
                pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
                cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
                for _ in range(int(Config().char["atk_len_pindle"])):
                    self._cast_foh(cast_pos_abs, spray=11)
                    self._cast_holy_bolt(cast_pos_abs, spray=80, time_in_s=int(Config().char["atk_len_pindle"])/2)
                wait(self._cast_duration, self._cast_duration + 0.2)

        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            if not self._do_pre_move:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.05, 0.15)
            self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, timeout=1.0, do_pre_move=self._do_pre_move)
        return True


    def kill_council(self) -> bool:
        # Attack towards stairs
        #trav_attack_pos = self._pather.find_abs_node_pos(225, grab())
        #Logger.info(f"trav_attack_pos: {trav_attack_pos}")
        #if trav_attack_pos is None:
        #    trav_attack_pos = self._pather.find_abs_node_pos(906, grab())
        #self._cast_foh(trav_attack_pos, spray=80, time_in_s=4)
        #self._cast_holy_bolt(trav_attack_pos, spray=80, time_in_s=4)
        atk_len_factor = 1
        atk_len = "atk_len_trav"
        atk_len_dur = int(Config().char[atk_len])*atk_len_factor
        if self._skill_hotkeys["conviction"]: keyboard.send(self._skill_hotkeys["conviction"]) #conviction needs to be on for mob_detection
        wait(1) #let merc cast holy freeze
        if (targets := get_visible_targets()):
            nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
            Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[96m'+" fisting him now "+ str(atk_len_dur) + " times!" +'\033[0m')
            for _ in range(atk_len_dur):
                self._cast_foh(nearest_mob_pos_abs, spray=11)
            #    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
            #wait(self._cast_duration, self._cast_duration + 0.2)
            if (targets := get_visible_targets()):
                nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
                Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[93m'+" bolting him now "+ str(atk_len_dur) + " seconds!" +'\033[0m')
                #print (nearest_mob_pos_abs)
                for _ in range(atk_len_dur):
                #    self._cast_foh(nearest_mob_pos_abs, spray=11)
                    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
                #wait(self._cast_duration, self._cast_duration + 0.2)
            else:
                Logger.debug("No Mob found, moving on")
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2) #clear yourself from curses
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.5, 1.0) #clear area from corpses & heal
        else:
            Logger.debug("No Mob found, moving on")


        self._pather.traverse_nodes([225], self, timeout=2.5, force_tp=True)
        if self._skill_hotkeys["conviction"]: keyboard.send(self._skill_hotkeys["conviction"]) #conviction needs to be on for mob_detection
        wait(1) #let merc cast holy freeze
        if (targets := get_visible_targets()):
            nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
            Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[96m'+" fisting him now "+ str(atk_len_dur) + " times!" +'\033[0m')
            for _ in range(atk_len_dur):
                self._cast_foh(nearest_mob_pos_abs, spray=11)
            #    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
            #wait(self._cast_duration, self._cast_duration + 0.2)
            if (targets := get_visible_targets()):
                nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
                Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[93m'+" bolting him now "+ str(atk_len_dur) + " seconds!" +'\033[0m')
                #print (nearest_mob_pos_abs)
                for _ in range(atk_len_dur):
                #    self._cast_foh(nearest_mob_pos_abs, spray=11)
                    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
                #wait(self._cast_duration, self._cast_duration + 0.2)
            else:
                Logger.debug("No Mob found, moving on")
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2) #clear yourself from curses
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.5, 1.0) #clear area from corpses & heal
        else:
            Logger.debug("No Mob found, moving on")


        self._pather.traverse_nodes([226], self, timeout=2.5, force_tp=True)
        if self._skill_hotkeys["conviction"]: keyboard.send(self._skill_hotkeys["conviction"]) #conviction needs to be on for mob_detection
        wait(1) #let merc cast holy freeze
        if (targets := get_visible_targets()):
            nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
            Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[96m'+" fisting him now "+ str(atk_len_dur) + " times!" +'\033[0m')
            for _ in range(atk_len_dur):
                self._cast_foh(nearest_mob_pos_abs, spray=11)
            #    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
            #wait(self._cast_duration, self._cast_duration + 0.2)
            if (targets := get_visible_targets()):
                nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
                Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[93m'+" bolting him now "+ str(atk_len_dur) + " seconds!" +'\033[0m')
                #print (nearest_mob_pos_abs)
                for _ in range(atk_len_dur):
                #    self._cast_foh(nearest_mob_pos_abs, spray=11)
                    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
                #wait(self._cast_duration, self._cast_duration + 0.2)
            else:
                Logger.debug("No Mob found, moving on")
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2) #clear yourself from curses
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.5, 1.0) #clear area from corpses & heal
        else:
            Logger.debug("No Mob found, moving on")

        self._pather.traverse_nodes([300], self, timeout=2.5, force_tp=True)
        if self._skill_hotkeys["conviction"]: keyboard.send(self._skill_hotkeys["conviction"]) #conviction needs to be on for mob_detection
        wait(1) #let merc cast holy freeze
        if (targets := get_visible_targets()):
            nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
            Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[96m'+" fisting him now "+ str(atk_len_dur) + " times!" +'\033[0m')
            for _ in range(atk_len_dur):
                self._cast_foh(nearest_mob_pos_abs, spray=11)
            #    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
            #wait(self._cast_duration, self._cast_duration + 0.2)
            if (targets := get_visible_targets()):
                nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
                Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[93m'+" bolting him now "+ str(atk_len_dur) + " seconds!" +'\033[0m')
                #print (nearest_mob_pos_abs)
                for _ in range(atk_len_dur):
                #    self._cast_foh(nearest_mob_pos_abs, spray=11)
                    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
                #wait(self._cast_duration, self._cast_duration + 0.2)
            else:
                Logger.debug("No Mob found, moving on")
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2) #clear yourself from curses
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.5, 1.0) #clear area from corpses & heal
        else:
            Logger.debug("No Mob found, moving on")

        # Move outside since the trav.py expects to start searching for items there if char can teleport
        self._pather.traverse_nodes([226], self, timeout=2.5, force_tp=True)
        return True


    """ DEFENSIVE VERSION FROM FAR AWAY
    def kill_eldritch(self) -> bool:
        eld_pos_abs = convert_screen_to_abs(Config().path["eldritch_end"][0])
        cast_pos_abs = [eld_pos_abs[0] * 0.9, eld_pos_abs[1] * 0.9]
        self._cast_foh(cast_pos_abs, spray=80, time_in_s=int(Config().char["atk_len_eldritch"]))
        for _ in range(int(Config().char["atk_len_eldritch"])):
            self._cast_holy_bolt(cast_pos_abs, spray=90, time_in_s=int(Config().char["atk_len_eldritch"]))
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        pos_m = convert_abs_to_monitor((70, -200))
        self.pre_move()
        self.move(pos_m, force_move=True)        
        self._pather.traverse_nodes(Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END)
        return True
    """
    

    def kill_eldritch(self) -> bool:
        if self.capabilities.can_teleport_natively:
            # Custom eld position for teleport that brings us closer to eld
            self._pather.traverse_nodes_fixed([(675, 30)], self)
            self._cast_foh((0,0), spray=11)
            atk_len_factor = 1
            atk_len = "atk_len_eldritch"
            atk_len_dur = int(Config().char[atk_len])*atk_len_factor
            if self._skill_hotkeys["conviction"]: keyboard.send(self._skill_hotkeys["conviction"]) #conviction needs to be on for mob_detection
            if (targets := get_visible_targets()):
                nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
                Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[96m'+" fisting him now "+ str(atk_len_dur) + " times!" +'\033[0m')
                for _ in range(atk_len_dur):
                    self._cast_foh(nearest_mob_pos_abs, spray=11)
                #    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
                #wait(self._cast_duration, self._cast_duration + 0.2)
                if (targets := get_visible_targets()):
                    nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
                    Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[93m'+" bolting him now "+ str(atk_len_dur) + " seconds!" +'\033[0m')
                    #print (nearest_mob_pos_abs)
                    for _ in range(atk_len_dur):
                    #    self._cast_foh(nearest_mob_pos_abs, spray=11)
                        self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
                    #wait(self._cast_duration, self._cast_duration + 0.2)
                else:
                    Logger.debug("No Mob found, moving on")
                if self._skill_hotkeys["cleansing"]:
                    keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2) #clear yourself from curses
                if self._skill_hotkeys["redemption"]:
                    keyboard.send(self._skill_hotkeys["redemption"])
                    wait(0.5, 1.0) #clear area from corpses & heal
            else:
                Logger.debug("No Mob found, moving on")
        else:
            if not self._do_pre_move:
                keyboard.send(self._skill_hotkeys["conviction"])
                wait(0.05, 0.15)
            self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, timeout=1.0, do_pre_move=self._do_pre_move, force_tp=True, use_tp_charge=True)
            self._cast_foh((0,0), spray=11)
            atk_len_factor = 1
            atk_len = "atk_len_eldritch"
            atk_len_dur = int(Config().char[atk_len])*atk_len_factor
            if self._skill_hotkeys["conviction"]: keyboard.send(self._skill_hotkeys["conviction"]) #conviction needs to be on for mob_detection
            if (targets := get_visible_targets()):
                nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
                Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[96m'+" fisting him now "+ str(atk_len_dur) + " times!" +'\033[0m')
                for _ in range(atk_len_dur):
                    self._cast_foh(nearest_mob_pos_abs, spray=11)
                #    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
                #wait(self._cast_duration, self._cast_duration + 0.2)
                if (targets := get_visible_targets()):
                    nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
                    Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[93m'+" bolting him now "+ str(atk_len_dur) + " seconds!" +'\033[0m')
                    #print (nearest_mob_pos_abs)
                    for _ in range(atk_len_dur):
                    #    self._cast_foh(nearest_mob_pos_abs, spray=11)
                        self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
                    #wait(self._cast_duration, self._cast_duration + 0.2)
                else:
                    Logger.debug("No Mob found, moving on")
                if self._skill_hotkeys["cleansing"]:
                    keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2) #clear yourself from curses
                if self._skill_hotkeys["redemption"]:
                    keyboard.send(self._skill_hotkeys["redemption"])
                    wait(0.5, 1.0) #clear area from corpses & heal
            else:
                Logger.debug("No Mob found, moving on")
        return True


    """ DEFENSIVE VERSION FROM FAR AWAY
    def kill_shenk(self) -> bool:
        shenk_pos_abs = self._pather.find_abs_node_pos(149, grab())
        if shenk_pos_abs is None:
            shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        self._cast_foh(cast_pos_abs, spray=80, time_in_s=int(Config().char["atk_len_shenk"]))
        for _ in range(int(Config().char["atk_len_shenk"])):
            self._cast_holy_bolt(cast_pos_abs, spray=90, time_in_s=int(Config().char["atk_len_shenk"]))
        pos_m = convert_abs_to_monitor((150, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        self._cast_foh(cast_pos_abs, spray=80, time_in_s=int(Config().char["atk_len_shenk"]))
        for _ in range(int(Config().char["atk_len_shenk"])):
            self._cast_holy_bolt(cast_pos_abs, spray=90, time_in_s=int(Config().char["atk_len_shenk"]))
        pos_m = convert_abs_to_monitor((150, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        self._cast_foh(cast_pos_abs, spray=80, time_in_s=int(Config().char["atk_len_shenk"]))
        for _ in range(int(Config().char["atk_len_shenk"])):
            self._cast_holy_bolt(cast_pos_abs, spray=90, time_in_s=int(Config().char["atk_len_shenk"]))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.4, force_tp=True)
        return True
    """


    def kill_shenk(self):
        if not self._do_pre_move:
            keyboard.send(self._skill_hotkeys["conviction"])
            wait(0.05, 0.15)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.0, do_pre_move=self._do_pre_move, force_tp=True, use_tp_charge=True)
        wait(0.05, 0.1)
        self._cast_foh((0, 0), spray=11)
        atk_len_factor = 1
        atk_len = "atk_len_shenk"
        atk_len_dur = int(Config().char[atk_len])*atk_len_factor
        if self._skill_hotkeys["conviction"]: keyboard.send(self._skill_hotkeys["conviction"]) #conviction needs to be on for mob_detection
        if (targets := get_visible_targets()):
            nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
            Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[96m'+" fisting him now "+ str(atk_len_dur) + " times!" +'\033[0m')
            for _ in range(atk_len_dur):
                self._cast_foh(nearest_mob_pos_abs, spray=11)
            #    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
            #wait(self._cast_duration, self._cast_duration + 0.2)
            if (targets := get_visible_targets()):
                nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
                Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[93m'+" bolting him now "+ str(atk_len_dur) + " seconds!" +'\033[0m')
                #print (nearest_mob_pos_abs)
                for _ in range(atk_len_dur):
                #    self._cast_foh(nearest_mob_pos_abs, spray=11)
                    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
                #wait(self._cast_duration, self._cast_duration + 0.2)
            else:
                Logger.debug("No Mob found, moving on")
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2) #clear yourself from curses
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.5, 1.0) #clear area from corpses & heal
        else:
            Logger.debug("No Mob found, moving on")
        return True


    """ DEFENSIVE VERSION FROM FAR AWAY
    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        delay = [0.2, 0.3]
        atk_len = int(Config().char["atk_len_nihlathak"])
        nihlathak_pos_abs = None
        for i in range(atk_len):
            nihlathak_pos_abs_next = self._pather.find_abs_node_pos(end_nodes[-1], grab())

            if nihlathak_pos_abs_next is not None:
                nihlathak_pos_abs = nihlathak_pos_abs_next
            else:
                Logger.warning(f"Can't find Nihlathak next position at node {end_nodes[-1]}")
                if nihlathak_pos_abs is not None:
                    Logger.warning(f"Using previous position for attack sequence")

            if nihlathak_pos_abs is not None:
                cast_pos_abs = np.array([nihlathak_pos_abs[0] * 0.9, nihlathak_pos_abs[1] * 0.9])
                self._cast_foh(cast_pos_abs, spray=80, time_in_s=int(Config().char["atk_len_nihlathak"]))
                self._cast_holy_bolt(cast_pos_abs, spray=90, time_in_s=int(Config().char["atk_len_nihlathak"]))
                # Do some tele "dancing" after each sequence
                if i < atk_len - 1:
                    rot_deg = random.randint(-10, 10) if i % 2 == 0 else random.randint(170, 190)
                    tele_pos_abs = unit_vector(rotate_vec(cast_pos_abs, rot_deg)) * 100
                    pos_m = convert_abs_to_monitor(tele_pos_abs)
                    self.pre_move()
                    self.move(pos_m)
                else:
                    self._cast_foh(cast_pos_abs, spray=80, time_in_s=int(Config().char["atk_len_nihlathak"]))
            else:
                Logger.warning(f"Casting FOH as the last position isn't known. Skipping attack sequence")
                self._cast_foh(cast_pos_abs, spray=80, time_in_s=int(Config().char["atk_len_nihlathak"]))

        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8)
        return True
    """

    """
    #aggressive version, right into the face!
    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Move close to nihlathak
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8, do_pre_move=False)
        self._cast_foh((0, 0), spray=11)
        atk_len_factor = 1
        atk_len = "atk_len_nihlathak"
        atk_len_dur = int(Config().char[atk_len])*atk_len_factor
        if self._skill_hotkeys["conviction"]: keyboard.send(self._skill_hotkeys["conviction"]) #conviction needs to be on for mob_detection
        if (targets := get_visible_targets()):
            nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
            Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[96m'+" fisting him now "+ str(atk_len_dur) + " times!" +'\033[0m')
            for _ in range(atk_len_dur):
                self._cast_foh(nearest_mob_pos_abs, spray=11)
            #    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
            #wait(self._cast_duration, self._cast_duration + 0.2)
            if (targets := get_visible_targets()):
                nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
                Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[96m'+" fisting him now "+ str(atk_len_dur) + " times!" +'\033[0m')
                Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[93m'+" bolting him now "+ str(atk_len_dur) + " seconds!" +'\033[0m')
                #print (nearest_mob_pos_abs)
                for _ in range(atk_len_dur):
                    self._cast_foh(nearest_mob_pos_abs, spray=11)
                    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
                #wait(self._cast_duration, self._cast_duration + 0.2)
            else:
                Logger.debug("No Mob found, moving on")
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2) #clear yourself from curses
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.5, 1.0) #clear area from corpses & heal
        else:
            Logger.debug("No Mob found, moving on")
        return True
    """
    #we just use hammers :)
    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Move close to nihlathak
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8, do_pre_move=False)
        # move mouse to center, otherwise hammers sometimes dont fly, not sure why
        pos_m = convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_hammers(Config().char["atk_len_nihlathak"] * 0.4)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((30, 15), Config().char["atk_len_nihlathak"] * 0.3)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((-30, -15), Config().char["atk_len_nihlathak"] * 0.4)
        wait(0.1, 0.15)
        self._cast_hammers(1.2, "redemption")
        return True

    def kill_summoner(self) -> bool:
        # Attack
        cast_pos_abs = np.array([0, 0])
        pos_m = convert_abs_to_monitor((-20, 20))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        for _ in range(int(Config().char["atk_len_arc"])):
            self._cast_foh(cast_pos_abs, spray=80, time_in_s=int(Config().char["atk_len_arc"]))
            self._cast_holy_bolt(cast_pos_abs, spray=90, time_in_s=int(Config().char["atk_len_arc"]))
        wait(self._cast_duration, self._cast_duration + 0.2)
        return True
    

     ########################################################################################
     # Chaos Sanctuary, Trash, Seal Bosses (a = Vizier, b = De Seis, c = Infector) & Diablo #
     ########################################################################################

    #FOHdin Attack Sequence Optimized for trash
    def cs_trash_atk_seq(self, atk_len, atk_len_factor):
        """
        :FOHdin Attack Sequence Optimized for killing trash in Chaos Sanctuary:
        :param atk_len: Attack Length as defined in Config
        :param atk_len_factor: Multiplier (int) for the Param atk_len to adapt length for locations with large number of mobs
        Returns True
        """
        self._cast_foh((0,0), spray=11) #never wrong to cast a FOH on yourself :)
        atk_len = int(Config().char[atk_len])*atk_len_factor
        if self._skill_hotkeys["conviction"]: keyboard.send(self._skill_hotkeys["conviction"]) #conviction needs to be on for mob_detection
        if (targets := get_visible_targets()):
            nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
            Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[96m'+" fisting him now "+ str(atk_len) + "times!" +'\033[0m')
            for _ in range(atk_len):
                self._cast_foh(nearest_mob_pos_abs, spray=11)
            #    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len)
            #wait(self._cast_duration, self._cast_duration + 0.2)
            if (targets := get_visible_targets()):
                nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
                Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[93m'+" bolting him now "+ str(atk_len) + "seconds!" +'\033[0m')
                #print (nearest_mob_pos_abs)
                for _ in range(atk_len):
                #    self._cast_foh(nearest_mob_pos_abs, spray=11)
                    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len)
                #wait(self._cast_duration, self._cast_duration + 0.2)
            else:
                Logger.debug("No Mob found, moving on")
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2) #clear yourself from curses
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.5, 1.0) #clear area from corpses & heal
        else:
            Logger.debug("No Mob found, moving on")
        return True

    def kill_cs_trash(self, location:str) -> bool:
        if not Config().char['cs_mob_detect']:
            Logger.error("This run requires 'cs_mob_detect' to be set to 1")
            return False

        ###########
        # SEALDANCE
        ###########

        #these locations have no traverses and are basically identical.
        #if location in ("sealdance", "rof_01", "rof_02", "entrance_hall_01", "entrance_hall_02", "entrance1_01", "entrance1_02", "entrance1_03", "entrance1_04", "entrance2_01", "entrance2_03"):

        if location == "sealdance": #if seal opening fails & trash needs to be cleared -> used at ANY seal
            ### APPROACH
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 3)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        ################
        # CLEAR CS TRASH
        ################

        elif location == "rof_01": #node 603 - outside CS in ROF
            ### APPROACH ###
            if not self._pather.traverse_nodes([603], self, timeout=3): return False #calibrate after static path
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([603], self): return False #calibrate after looting


        elif location == "rof_02": #node 604 - inside ROF
            ### APPROACH ###
            if not self._pather.traverse_nodes([604], self, timeout=3): return False  #threshold=0.8 (ex 601)
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance_hall_01": ##static_path "diablo_entrance_hall_1", node 677, CS Entrance Hall1
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("diablo_entrance_hall_1", self) # 604 -> 671 Hall1
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance_hall_02":  #node 670,671, CS Entrance Hall1, CS Entrance Hall1
            ### APPROACH ###
            if not self._pather.traverse_nodes([670], self): return False # pull top mobs 672 to bottom 670
            self._pather.traverse_nodes_fixed("diablo_entrance_1_670_672", self) # 604 -> 671 Hall1
            if not self._pather.traverse_nodes([670], self): return False # pull top mobs 672 to bottom 670
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)            #Move to Layout Check
            if not self._pather.traverse_nodes([671], self): return False # calibrate before static path
            self._pather.traverse_nodes_fixed("diablo_entrance_hall_2", self) # 671 -> LC Hall2



        # TRASH LAYOUT A

        elif location == "entrance1_01": #static_path "diablo_entrance_hall_2", Hall1 (before layout check)
            ### APPROACH ###
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)            
            if not self._pather.traverse_nodes([673], self): return False # , timeout=3): # Re-adjust itself and continues to attack

        elif location == "entrance1_02": #node 673
            ### APPROACH ###
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)            
            self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self) # Moves char to postion close to node 674 continues to attack
            if not self._pather.traverse_nodes([674], self): return False#, timeout=3)

        elif location == "entrance1_03": #node 674
            ### APPROACH ###
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)                
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([675], self): return False#, timeout=3) # Re-adjust itself
            self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self) #static path to get to be able to spot 676
            if not self._pather.traverse_nodes([676], self): return False#, timeout=3)

        elif location == "entrance1_04": #node 676- Hall3
            ### APPROACH ###
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        
        # TRASH LAYOUT B

        elif location == "entrance2_01": #static_path "diablo_entrance_hall_2"
            ### APPROACH ###
                       ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance2_02": #node 682
            ### APPROACH ###
            #if not self._pather.traverse_nodes([682], self): return False # , timeout=3):
            if self._skill_hotkeys["conviction"]: keyboard.send(self._skill_hotkeys["conviction"]) #conviction needs to be on for mob_detection
            if (targets := get_visible_targets()):
                nearest_mob_pos_abs = convert_screen_to_abs(targets[0].center)
                print (nearest_mob_pos_abs)
                for _ in range(int(Config().char["atk_len_cs_trashmobs"])*2):
                    self._cast_foh(nearest_mob_pos_abs, spray=11)
                    self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=int(Config().char["atk_len_cs_trashmobs"])*2)
                wait(self._cast_duration, self._cast_duration + 0.2)
                if self._skill_hotkeys["cleansing"]:
                    keyboard.send(self._skill_hotkeys["cleansing"])
                    wait(0.1, 0.2)
                if self._skill_hotkeys["redemption"]:
                    keyboard.send(self._skill_hotkeys["redemption"])
                    wait(0.3, 0.6)
                ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance2_03": #node 683
            ### APPROACH ###
            #if not self._pather.traverse_nodes([682], self): return False # , timeout=3):
            #self._pather.traverse_nodes_fixed("diablo_entrance2_1", self)
            #if not self._pather.traverse_nodes([683], self): return False # , timeout=3):
            self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_top1", self) #pull mobs from top
            wait (0.2, 0.5)
            self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_top2", self) #pull mobs from top
            if not self._pather.traverse_nodes([605], self): return False#, timeout=3)
                       ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance2_04": #node 686 - Hall3
            ### APPROACH ###
            if not self._pather.traverse_nodes([605], self): return False#, timeout=3)
            #if not self._pather.traverse_nodes([683,684], self): return False#, timeout=3)
            #self._pather.traverse_nodes_fixed("diablo_entrance2_2", self)
            #if not self._pather.traverse_nodes([685,686], self): return False#, timeout=3)
            self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_hall3", self)
            if not self._pather.traverse_nodes([609], self): return False#, timeout=3)
            self._pather.traverse_nodes_fixed("diablo_trash_b_hall3_pull_609", self)
            if not self._pather.traverse_nodes([609], self): return False#, timeout=3)
                       ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)                
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([609], self): return False#, timeout=3)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([609], self): return False#, timeout=3)

        ####################
        # PENT TRASH TO SEAL
        ####################

        elif location == "dia_trash_a": #trash before between Pentagramm and Seal A Layoutcheck
            ### APPROACH ###
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        elif location == "dia_trash_b": #trash before between Pentagramm and Seal B Layoutcheck
            ### APPROACH ###
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        elif location == "dia_trash_c": ##trash before between Pentagramm and Seal C Layoutcheck
            ### APPROACH ###
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        ###############
        # LAYOUT CHECKS
        ###############

        elif location == "layoutcheck_a": #layout check seal A, node 619 A1-L, node 620 A2-Y
            ### APPROACH ###
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)            #Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "layoutcheck_b": #layout check seal B, node 634 B1-S, node 649 B2-U
            ### APPROACH ###
                ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        elif location == "layoutcheck_c": #layout check seal C, node 656 C1-F, node 664 C2-G
            ### APPROACH ###
            ## ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        ##################
        # PENT BEFORE SEAL
        ##################

        elif location == "pent_before_a": #node 602, pentagram, before CTA buff & depature to layout check - not needed when trash is skipped & seals run in right order
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "pent_before_b": #node 602, pentagram, before CTA buff & depature to layout check
            ### APPROACH ###
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        elif location == "pent_before_c": #node 602, pentagram, before CTA buff & depature to layout check
            ### APPROACH ###
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        ###########
        # SEAL A1-L
        ###########

        elif location == "A1-L_01":  #node 611 seal layout A1-L: safe_dist
            ### APPROACH ###
            if not self._pather.traverse_nodes([611], self): return False # , timeout=3):
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            # we loot at boss

        elif location == "A1-L_02":  #node 612 seal layout A1-L: center
            ### APPROACH ###
            if not self._pather.traverse_nodes([612], self): return False # , timeout=3):
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            # we loot at boss

        elif location == "A1-L_03":  #node 613 seal layout A1-L: fake_seal
            ### APPROACH ###
            if not self._pather.traverse_nodes([613], self): return False # , timeout=3):
                       ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "A1-L_seal1":  #node 613 seal layout A1-L: fake_seal
            ### APPROACH ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([614], self): return False
            ### ATTACK ###
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            # we loot at boss

        elif location == "A1-L_seal2":  #node 614 seal layout A1-L: boss_seal
            ### APPROACH ###
            if not self._pather.traverse_nodes([613, 615], self): return False # , timeout=3):
            ### ATTACK ###
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            # we loot at boss

        ###########
        # SEAL A2-Y
        ###########

        elif location == "A2-Y_01":  #node 622 seal layout A2-Y: safe_dist
            ### APPROACH ###
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.debug("A2-Y: Hop!")
            #if not self._pather.traverse_nodes([622], self): return False # , timeout=3):
            if not self._pather.traverse_nodes([622], self): return False
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            # we loot at boss

        elif location == "A2-Y_02":  #node 623 seal layout A2-Y: center
            ### APPROACH ###
            # if not self._pather.traverse_nodes([623,624], self): return False #
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)            
            ### LOOT ###
            # we loot at boss

        elif location == "A2-Y_03": #skipped
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "A2-Y_seal1":  #node 625 seal layout A2-Y: fake seal
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            if not self._pather.traverse_nodes([625], self): return False # , timeout=3):
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)

        elif location == "A2-Y_seal2":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            self._pather.traverse_nodes_fixed("dia_a2y_sealfake_sealboss", self) #instead of traversing node 626 which causes issues
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)

        ###########
        # SEAL B1-S
        ###########

        elif location == "B1-S_01":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B1-S_02":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B1-S_03":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B1-S_seal2": #B only has 1 seal, which is the boss seal = seal2
            ### APPROACH ###
            if not self._pather.traverse_nodes([634], self): return False # , timeout=3):
            ### ATTACK ###
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###


        ###########
        # SEAL B2-U
        ###########

        elif location == "B2-U_01":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B2-U_02":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B2-U_03":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B2-U_seal2": #B only has 1 seal, which is the boss seal = seal2
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_b2u_bold_seal", self)
            if not self._pather.traverse_nodes([644], self): return False # , timeout=3):
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)


        ###########
        # SEAL C1-F
        ###########

        elif location == "C1-F_01":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C1-F_02":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C1-F_03":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C1-F_seal1":
            ### APPROACH ###
            wait(0.1,0.3)
            self._pather.traverse_nodes_fixed("dia_c1f_hop_fakeseal", self)
            wait(0.1,0.3)
            if not self._pather.traverse_nodes([655], self): return False # , timeout=3):
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)                
            if not self._pather.traverse_nodes([655], self): return False # , timeout=3):
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)

        elif location == "C1-F_seal2":
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_c1f_654_651", self)
            if not self._pather.traverse_nodes([652], self): return False # , timeout=3):
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)                
            if not self._pather.traverse_nodes([652], self): return False # , timeout=3):
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)

        ###########
        # SEAL C2-G
        ###########

        elif location == "C2-G_01": #skipped
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C2-G_02": #skipped
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C2-G_03": #skipped
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C2-G_seal1":
            ### APPROACH ###
            #if not self._pather.traverse_nodes([663, 662], self): return False # , timeout=3): #caused 7% failed runs, replaced by static path.
            self._pather.traverse_nodes_fixed("dia_c2g_lc_661", self)
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")


        elif location == "C2-G_seal2":
            ### APPROACH ###
            # Killing infector here, because for C2G its the only seal where a bossfight occures BETWEEN opening seals
            seal_layout="C2-G"
            self._pather.traverse_nodes_fixed("dia_c2g_663", self)
            ### ATTACK ###
            Logger.debug(seal_layout + ": Attacking Infector at position 1/1")
            self.cs_trash_atk_seq("atk_len_diablo_infector", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([664, 665], self): return False # , timeout=3):

        else:
            ### APPROACH ###
            Logger.warning("I have no location argument given for kill_cs_trash(" + location + "), should not happen. Throwing some random hammers")
            ### ATTACK ###
            self.cs_trash_atk_seq("atk_len_cs_trashmobs", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)        
            return True


    def kill_vizier(self, seal_layout:str) -> bool:
        if seal_layout == "A1-L":
            ### APPROACH ###
            if not self._pather.traverse_nodes([612], self): return False # , timeout=3):
            ### ATTACK ###
            Logger.debug(seal_layout + ": Attacking Vizier at position 1/2")
            self.cs_trash_atk_seq("atk_len_diablo_vizier", 1)
            Logger.debug(seal_layout + ": Attacking Vizier at position 2/2")
            self._pather.traverse_nodes([611], self, timeout=3)
            self.cs_trash_atk_seq("atk_len_diablo_vizier", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([612], self): return False # , timeout=3):
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([612], self): return False # , timeout=3): # recalibrate after loot

        elif seal_layout == "A2-Y":
            ### APPROACH ###
            if not self._pather.traverse_nodes([627, 622], self): return False # , timeout=3):
            ### ATTACK ###
            Logger.debug(seal_layout + ": Attacking Vizier at position 1/2")
            self.cs_trash_atk_seq("atk_len_diablo_vizier", 1)
            Logger.debug(seal_layout + ": Attacking Vizier at position 2/2")
            self._pather.traverse_nodes([623], self, timeout=3)
            self.cs_trash_atk_seq("atk_len_diablo_vizier", 1)
            Logger.debug(seal_layout + ": Attacking Vizier at position 3/3")
            if not self._pather.traverse_nodes([624], self): return False
            self.cs_trash_atk_seq("atk_len_diablo_vizier", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([624], self): return False
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.debug(seal_layout + ": Hop!")
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            if not self._pather.traverse_nodes([622], self): return False #, timeout=3):
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([622], self): return False # , timeout=3): #recalibrate after loot

        else:
            Logger.warning(seal_layout + ": Invalid location for kill_deseis("+ seal_layout +"), should not happen.")
            return False
        return True

### STOP HERE ###

    def kill_deseis(self, seal_layout:str) -> bool:
        if seal_layout == "B1-S":
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_b1s_seal_deseis", self) # quite aggressive path, but has high possibility of directly killing De Seis with first hammers, for 50% of his spawn locations
            nodes1 = [632]
            nodes2 = [631]
            nodes3 = [632]
            ### ATTACK ###
            Logger.debug(seal_layout + ": Attacking De Seis at position 1/4")
            self.cs_trash_atk_seq("atk_len_diablo_deseis", 1)
            Logger.debug(seal_layout + ": Attacking De Seis at position 2/4")
            self._pather.traverse_nodes(nodes1, self, timeout=3)
            self.cs_trash_atk_seq("atk_len_diablo_deseis", 1)
            Logger.debug(seal_layout + ": Attacking De Seis at position 3/4")
            self._pather.traverse_nodes(nodes2, self, timeout=3)
            self.cs_trash_atk_seq("atk_len_diablo_deseis", 1)
            Logger.debug(seal_layout + ": Attacking De Seis at position 4/4")
            self._pather.traverse_nodes(nodes3, self, timeout=3)
            self.cs_trash_atk_seq("atk_len_diablo_deseis", 1)
            wait(2.5, 3.5) # to keep redemption on for a couple of seconds before the next teleport to have more corpses cleared & increase chance to find next template
            Logger.debug(seal_layout + ": Waiting with Redemption active to clear more corpses.")
            #if Config().general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/info_check_deseis_dead" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif seal_layout == "B2-U":
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_b2u_644_646", self) # We try to breaking line of sight, sometimes makes De Seis walk into the hammercloud. A better attack sequence here could make sense.
            #self._pather.traverse_nodes_fixed("dia_b2u_seal_deseis", self) # We try to breaking line of sight, sometimes makes De Seis walk into the hammercloud. A better attack sequence here could make sense.
            nodes1 = [640]
            nodes2 = [646]
            nodes3 = [641]
            ### ATTACK ###
            Logger.debug(seal_layout + ": Attacking De Seis at position 1/4")
            self.cs_trash_atk_seq("atk_len_diablo_deseis", 1)
            Logger.debug(seal_layout + ": Attacking De Seis at position 2/4")
            self._pather.traverse_nodes(nodes1, self, timeout=3)
            self.cs_trash_atk_seq("atk_len_diablo_deseis", 1)
            Logger.debug(seal_layout + ": Attacking De Seis at position 3/4")
            self._pather.traverse_nodes(nodes2, self, timeout=3)
            self.cs_trash_atk_seq("atk_len_diablo_deseis", 1)
            Logger.debug(seal_layout + ": Attacking De Seis at position 4/4")
            self._pather.traverse_nodes(nodes3, self, timeout=3)
            self.cs_trash_atk_seq("atk_len_diablo_deseis", 1)
            #if Config().general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/info_check_deseis_dead" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([641], self): return False # , timeout=3):
            if not self._pather.traverse_nodes([646], self): return False # , timeout=3):
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([646], self): return False # , timeout=3):
            if not self._pather.traverse_nodes([640], self): return False # , timeout=3):
            self._picked_up_items |= self._pickit.pick_up_items(self)

        else:
            Logger.warning(seal_layout + ": Invalid location for kill_deseis("+ seal_layout +"), should not happen.")
            return False
        return True



    def kill_infector(self, seal_layout:str) -> bool:
        if seal_layout == "C1-F":
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_c1f_652", self)
            ### ATTACK ###
            Logger.debug(seal_layout + ": Attacking Infector at position 1/1")
            self.cs_trash_atk_seq("atk_len_diablo_infector", 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif seal_layout == "C2-G":
            # NOT killing infector here, because for C2G its the only seal where a bossfight occures BETWEEN opening seals his attack sequence can be found in C2-G_seal2
            Logger.debug(seal_layout + ": No need for attacking Infector at position 1/1 - he was killed during clearing the seal")

        else:
            Logger.warning(seal_layout + ": Invalid location for kill_infector("+ seal_layout +"), should not happen.")
            return False
        return True

    
    #no aura effect on dia. not good for mob detection
    def kill_diablo(self) -> bool:
        ### APPROACH ###
        ### ATTACK ###
        pos_m = convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        Logger.debug("Attacking Diablo at position 1/1")
        atk_len_factor = 1
        atk_len = "atk_len_diablo"
        atk_len_dur = int(Config().char[atk_len])*atk_len_factor
        if self._skill_hotkeys["conviction"]: keyboard.send(self._skill_hotkeys["conviction"]) #conviction needs to be on for mob_detection
        nearest_mob_pos_abs = [100,-100] #hardcoded dia pos.
        Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[96m'+" fisting him now "+ str(atk_len_dur) + "times!" +'\033[0m')
        for _ in range(atk_len_dur):
            self._cast_foh(nearest_mob_pos_abs, spray=11)
            Logger.debug("Mob found at " + str(nearest_mob_pos_abs) + '\033[93m'+" bolting him now "+ str(atk_len_dur) + "seconds!" +'\033[0m')
            self._cast_holy_bolt(nearest_mob_pos_abs, spray=80, time_in_s=atk_len_dur)
        if self._skill_hotkeys["cleansing"]:
            keyboard.send(self._skill_hotkeys["cleansing"])
        wait(0.1, 0.2) #clear yourself from curses
        if self._skill_hotkeys["redemption"]:
            keyboard.send(self._skill_hotkeys["redemption"])
            wait(0.5, 1.0) #clear area from corpses & heal
        #
        Logger.debug("Lets mobcheck for safety reasons & hope in that second we have posion nova active")
        self.cs_trash_atk_seq("atk_len_diablo", 1)
        ### LOOT ###
        self._picked_up_items |= self._pickit.pick_up_items(self)
        return True
        
    """
    def kill_diablo(self) -> bool:
        ### APPROACH ###
        ### ATTACK ###
        pos_m = convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        Logger.debug("Attacking Diablo at position 1/1")
        self._cast_hammers(Config().char["atk_len_diablo"])
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((60, 30), Config().char["atk_len_diablo"])
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((-60, -30), Config().char["atk_len_diablo"])
        wait(0.1, 0.15)
        self._cast_hammers(1.2, "redemption")
        ### LOOT ###
        self._picked_up_items |= self._pickit.pick_up_items(self)
        return True
    """