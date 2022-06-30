import keyboard
from utils.custom_mouse import mouse
from char import IChar
import template_finder
from pather import Pather
from logger import Logger
from screen import grab
from config import Config
from utils.misc import wait, rotate_vec, unit_vector
import random
from pather import Location, Pather
import screen as screen
import numpy as np
import time
import os
from ui_manager import get_closest_non_hud_pixel
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab
from target_detect import get_visible_green_targets, get_visible_targets, get_visible_blue_targets

class Poison_Necro(IChar):
    def __init__(self, skill_hotkeys: dict, pather: Pather):
        os.system('color')
        Logger.info("\033[94m<<Setting up Necro>>\033[0m")
        super().__init__(skill_hotkeys)
        self._pather = pather
        #custom necro pathing for pindle
        self._pather.adapt_path((Location.A5_PINDLE_START, Location.A5_PINDLE_SAFE_DIST), [100,101])
        self._pather.adapt_path((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), [104])
        #minor offsets to pindle fight locations
        self._pather.offset_node(102, [15, 0])
        self._pather.offset_node(103, [15, 0])
        self._pather.offset_node(101, [100,-5])

        #Diablo
        self._pather.offset_node(644, [150, -70])
        self._pather.offset_node(610620, [50, 50])
        self._pather.offset_node(631, [-50, 50])
        self._pather.offset_node(656, [-70, -50])

        self._shenk_dead = 0
        self._skeletons_count=0
        self._mages_count=0
        self._golem_count="none"
        self._revive_count=0

    def poison_nova(self, time_in_s: float):
        if not self._skill_hotkeys["poison_nova"]:
            raise ValueError("You did not set poison nova hotkey!")
        keyboard.send(self._skill_hotkeys["poison_nova"])
        wait(0.05, 0.1)
        start = time.time()
        while (time.time() - start) < time_in_s:
            wait(0.03, 0.04)
            mouse.press(button="right")
            wait(0.12, 0.2)
            mouse.release(button="right")
            mouse.release(button="right")


    def pre_buff(self):
        #only CTA if pre trav
        if Config().char["cta_available"]:
            self._pre_buff_cta()
        if self._shenk_dead==1:
            Logger.info("trav buff?")
            #self._heart_of_wolverine()
        Logger.info("prebuff/cta")


    def _heart_of_wolverine(self):
        Logger.info('\033[94m'+"buff ~> heart_of_wolverine"+'\033[0m')
        keyboard.send(self._skill_hotkeys["heart_of_wolverine"])
        wait(0.05, 0.2)
        mouse.click(button="right")
        wait(self._cast_duration)

    def _clay_golem(self):
        Logger.info('\033[94m'+"cast ~> clay golem"+'\033[0m')
        keyboard.send(self._skill_hotkeys["clay_golem"])
        wait(0.05, 0.2)
        mouse.click(button="right")
        wait(self._cast_duration)

    def amp_dmg(self, hork_time: int):
        wait(0.5)
        if self._skill_hotkeys["amp_dmg"]:
            keyboard.send(self._skill_hotkeys["amp_dmg"])
            wait(0.5, 0.15)
        pos_m = convert_abs_to_monitor((0, -20))
        mouse.move(*pos_m)
        wait(0.5, 0.15)
        mouse.press(button="right")
        wait(hork_time)
        mouse.release(button="right") 

    def bone_armor(self):
        if self._skill_hotkeys["bone_armor"]:
            keyboard.send(self._skill_hotkeys["bone_armor"])
            wait(0.04, 0.1)
            mouse.click(button="right")
            wait(self._cast_duration)
        if self._skill_hotkeys["clay_golem"]:
            keyboard.send(self._skill_hotkeys["clay_golem"])
            wait(0.04, 0.1)
            mouse.click(button="right")
            wait(self._cast_duration)

    def _bone_armor(self):
        if self._skill_hotkeys["bone_armor"]:
            keyboard.send(self._skill_hotkeys["bone_armor"])
            wait(0.04, 0.1)
            mouse.click(button="right")
            wait(self._cast_duration)



    def _left_attack(self, cast_pos_abs: tuple[float, float], spray: int = 10):
        keyboard.send(Config().char["stand_still"], do_release=False)
        if self._skill_hotkeys["skill_left"]:
            keyboard.send(self._skill_hotkeys["skill_left"])
        for _ in range(10):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(0.25, 0.3)
            mouse.release(button="left")

        keyboard.send(Config().char["stand_still"], do_press=False)

    def _left_attack_single(self, cast_pos_abs: tuple[float, float], spray: int = 10, cast_count: int=6):
        keyboard.send(Config().char["stand_still"], do_release=False)
        if self._skill_hotkeys["skill_left"]:
            keyboard.send(self._skill_hotkeys["skill_left"])
        for _ in range(cast_count):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(0.25, 0.3)
            mouse.release(button="left")

        keyboard.send(Config().char["stand_still"], do_press=False)

    def _do_curse(self, hork_time: int):
        wait(0.5)
        if self._skill_hotkeys["curse"]:
            keyboard.send(self._skill_hotkeys["curse"])
            wait(0.05, 0.15)
        pos_m = convert_abs_to_monitor((0, -20))
        mouse.move(*pos_m)
        wait(0.05, 0.15)
        mouse.press(button="right")
        wait(hork_time)
        mouse.release(button="right") 

    def _force_teleport(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if not self._skill_hotkeys["force_teleport"]:
            raise ValueError("You did not set a hotkey for force_teleport!")
        keyboard.send(self._skill_hotkeys["force_teleport"])
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        click_tries = random.randint(2, 4)
        for _ in range(click_tries):
            mouse.press(button="right")
            wait(0.09, 0.12)
            mouse.release(button="right")            

    def _raise_skeleton(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if not self._skill_hotkeys["raise_skeleton"]:
            raise ValueError("You did not set a hotkey for raise_skeleton!")
        keyboard.send(self._skill_hotkeys["raise_skeleton"])
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        click_tries = random.randint(2, 4)
        for _ in range(click_tries):
            mouse.press(button="right")
            wait(0.09, 0.12)
            mouse.release(button="right") 


    def corpse_explosion(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if not self._skill_hotkeys["corpse_explosion"]:
            raise ValueError("You did not set a hotkey for corpse_explosion!")
        keyboard.send(self._skill_hotkeys["corpse_explosion"])
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        click_tries = random.randint(2, 4)
        for _ in range(click_tries):
            mouse.press(button="right")
            wait(0.09, 0.12)
            mouse.release(button="right") 

    def _raise_mage(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.2, 0.3), spray: float = 10):
        if not self._skill_hotkeys["raise_mage"]:
            raise ValueError("You did not set raise_mage hotkey!")
        keyboard.send(self._skill_hotkeys["raise_mage"])
        for _ in range(3):
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor, delay_factor=[0.3, 0.6])
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")

    def _raise_revive(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if not self._skill_hotkeys["raise_revive"]:
            raise ValueError("You did not set a hotkey for raise_revive!")
        keyboard.send(self._skill_hotkeys["raise_revive"])
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        click_tries = random.randint(2, 4)
        for _ in range(click_tries):
            mouse.press(button="right")
            wait(0.09, 0.12)
            mouse.release(button="right")        

    def _pn_attack_sequence(
        self,
        default_target_abs: tuple[int, int] = (-50, -50),
        min_duration: float = 0,
        max_duration: float = 15,
        blizz_to_ice_blast_ratio: int = 3,
        target_detect: bool = True,
        default_spray: int = 20,
        #aura: str = ""
    ) -> bool:
        start = time.time()
        target_check_count = 1
        #foh_aura = aura if aura else "conviction"
        #holy_bolt_aura = aura if aura else "concentration"
        while (elapsed := (time.time() - start)) <= max_duration:
            cast_pos_abs = default_target_abs
            spray = default_spray
            atk_len = Config().char["atk_len_cs_trashmobs"] * .50
            # if targets are detected, switch to targeting with reduced spread rather than present default cast position and default spread
            if target_detect and (targets := get_visible_green_targets()):
                # log_targets(targets)
                spray = 5
                cast_pos_abs = targets[0].center_abs
                target_check_count += 1
                closest_target_position_monitor = targets[0].center_monitor



            # if time > minimum and either targets aren't set or targets don't exist, exit loop
            if elapsed > min_duration and (not target_detect or not targets):
                break

            targets = get_visible_green_targets()
            if targets and len(targets) > 0:
                # TODO: add delay between FOH casts--doesn't properly cast each FOH in sequence
                # cast foh to holy bolt with preset ratio (e.g. 3 foh followed by 1 holy bolt if foh_to_holy_bolt_ratio = 3)
                    Logger.info("Mob detected, Attacking mobs!")
                    self.poison_nova(atk_len)
                    self._raise_skeleton(cast_pos_abs, spray=spray)
                    #self._raise_mage(cast_pos_abs, spray=spray)
                    self._raise_revive(cast_pos_abs, spray=spray)
                    targets = get_visible_green_targets()
                    if targets:
                        closest_target_position_monitor = targets[0].center_monitor
                        self.pre_move()
                        self.move(closest_target_position_monitor, force_move=True)
                    pos_m = screen.convert_abs_to_monitor((50, 0))
                    self.walk(pos_m, force_move=True)
                    self.poison_nova(atk_len)
                    targets = get_visible_green_targets()                    
                    self._raise_revive(cast_pos_abs, spray=spray)
                    self._raise_mage(cast_pos_abs, spray=spray)
                    self._raise_skeleton(cast_pos_abs, spray=spray)

            else:
                    Logger.info("No minions detected yet, Default attack sequence")
                    targets = get_visible_green_targets()
                    self.poison_nova(atk_len)
                    targets = get_visible_green_targets() 
                    self._raise_skeleton((-25, -75), spray=50)
                    pos_m = screen.convert_abs_to_monitor((0, 30))
                    self.walk(pos_m, force_move=True)                   
                    self._raise_revive((-35, -50), spray=50)
                    self._raise_mage((0, -100), spray=50)
                    self._raise_skeleton(cast_pos_abs, spray=spray)                    


            target_check_count += 1
        return True


    def _trav_attack(
        self,
        default_target_abs: tuple[int, int] = (-50, -50),
        min_duration: float = 0,
        max_duration: float = 15,
        blizz_to_ice_blast_ratio: int = 3,
        target_detect: bool = True,
        default_spray: int = 20,
        #aura: str = ""
    ) -> bool:
        start = time.time()
        target_check_count = 1
        #foh_aura = aura if aura else "conviction"
        #holy_bolt_aura = aura if aura else "concentration"
        while (elapsed := (time.time() - start)) <= max_duration:
            cast_pos_abs = default_target_abs
            spray = default_spray
            atk_len = Config().char["atk_len_cs_trashmobs"] * .50
            # if targets are detected, switch to targeting with reduced spread rather than present default cast position and default spread
            if target_detect and (targets := get_visible_targets()):
                # log_targets(targets)
                spray = 5
                cast_pos_abs = targets[0].center_abs
                target_check_count += 1
                closest_target_position_monitor = targets[0].center_monitor



            # if time > minimum and either targets aren't set or targets don't exist, exit loop
            if elapsed > min_duration and (not target_detect or not targets):
                break

            targets = get_visible_targets()
            if targets and len(targets) > 0:
                # TODO: add delay between FOH casts--doesn't properly cast each FOH in sequence
                # cast foh to holy bolt with preset ratio (e.g. 3 foh followed by 1 holy bolt if foh_to_holy_bolt_ratio = 3)
                    Logger.info("Mob detected, Attacking mobs!")
                    self.poison_nova(atk_len)
                    #self._raise_revive(cast_pos_abs, spray=spray)
                    self.corpse_explosion(cast_pos_abs, spray=spray) 
                    targets = get_visible_targets()
                    if targets:
                        Logger.info("Teleporting to mob!")
                        closest_target_position_monitor = targets[0].center_monitor
                        self.pre_move()
                        self.move(closest_target_position_monitor, force_move=True)
                    pos_m = screen.convert_abs_to_monitor((50, 0))
                    self.walk(pos_m, force_move=True)
                    self.poison_nova(atk_len)
                    targets = get_visible_targets()
                    self.corpse_explosion(cast_pos_abs, spray=spray)    
                    if targets:
                        closest_target_position_monitor = targets[0].center_monitor
                        self.pre_move()
                        self.move(closest_target_position_monitor, force_move=True)
                    pos_m = screen.convert_abs_to_monitor((-50, 0))
                    self.walk(pos_m, force_move=True)
                    self.corpse_explosion(cast_pos_abs, spray=spray)                    
                    self._raise_revive(cast_pos_abs, spray=spray)
                    #self._raise_mage(cast_pos_abs, spray=spray)
                    self._raise_skeleton(cast_pos_abs, spray=spray)
                    self.corpse_explosion(cast_pos_abs, spray=spray)

            else:
                    Logger.info("No minions detected yet, Default attack sequence")
                    targets = get_visible_targets()
                    self.poison_nova(atk_len)
                    targets = get_visible_targets()
                    self.corpse_explosion(cast_pos_abs, spray=spray)                    
                    #self._raise_revive(cast_pos_abs, spray=spray)
                    self._raise_mage(cast_pos_abs, spray=spray)
                    self._raise_skeleton(cast_pos_abs, spray=spray)
                    self.corpse_explosion(cast_pos_abs, spray=spray)

            target_check_count += 1
        return True        
    
    def _nihl_attack(
        self,
        default_target_abs: tuple[int, int] = (-50, -50),
        min_duration: float = 0,
        max_duration: float = 15,
        blizz_to_ice_blast_ratio: int = 3,
        target_detect: bool = True,
        default_spray: int = 20,
        #aura: str = ""
    ) -> bool:
        start = time.time()
        target_check_count = 1
        #foh_aura = aura if aura else "conviction"
        #holy_bolt_aura = aura if aura else "concentration"
        while (elapsed := (time.time() - start)) <= max_duration:
            cast_pos_abs = default_target_abs
            spray = default_spray
            atk_len = Config().char["atk_len_nihlathak"] * .50
            # if targets are detected, switch to targeting with reduced spread rather than present default cast position and default spread
            if target_detect and (targets := get_visible_targets()):
                # log_targets(targets)
                spray = 5
                cast_pos_abs = targets[0].center_abs
                target_check_count += 1
                closest_target_position_monitor = targets[0].center_monitor



            # if time > minimum and either targets aren't set or targets don't exist, exit loop
            if elapsed > min_duration and (not target_detect or not targets):
                break

            targets = get_visible_targets()
            if targets and len(targets) > 0:
                # TODO: add delay between FOH casts--doesn't properly cast each FOH in sequence
                # cast foh to holy bolt with preset ratio (e.g. 3 foh followed by 1 holy bolt if foh_to_holy_bolt_ratio = 3)
                    Logger.info("Mob detected, Attacking mobs!")
                    self.poison_nova(1.5)
                    #self._raise_revive(cast_pos_abs, spray=spray)
                    targets = get_visible_targets()
                    self.corpse_explosion(cast_pos_abs, spray=spray)                    
                    targets = get_visible_targets()
                    self.corpse_explosion(cast_pos_abs, spray=spray) 
                    targets = get_visible_targets()
                    self.corpse_explosion(cast_pos_abs, spray=spray) 
                    if targets:
                        Logger.info("Teleporting to mob!")
                        closest_target_position_monitor = targets[0].center_monitor
                        self.pre_move()
                        self.move(closest_target_position_monitor, force_move=True)
                    self.poison_nova(1.5)
                    targets = get_visible_targets()
                    self.corpse_explosion(cast_pos_abs, spray=spray)                    
                    targets = get_visible_targets()
                    self.corpse_explosion(cast_pos_abs, spray=spray) 
            else:
                    Logger.info("No minions detected yet, Default attack sequence")
                    targets = get_visible_targets()
                    self.poison_nova(1.5)
                    targets = get_visible_targets()
                    self.corpse_explosion(cast_pos_abs, spray=spray)                    
                    targets = get_visible_targets()
                    self.corpse_explosion(cast_pos_abs, spray=spray)
                    targets = get_visible_targets()
                    self.corpse_explosion(cast_pos_abs, spray=spray)                    
                    targets = get_visible_targets()
                    self.corpse_explosion(cast_pos_abs, spray=spray)  

            target_check_count += 1
        return True        
    
    def _pindle_attack(
        self,
        default_target_abs: tuple[int, int] = (-50, -50),
        min_duration: float = 0,
        max_duration: float = 15,
        blizz_to_ice_blast_ratio: int = 3,
        target_detect: bool = True,
        default_spray: int = 20,
        #aura: str = ""
    ) -> bool:
        start = time.time()
        target_check_count = 1
        #foh_aura = aura if aura else "conviction"
        #holy_bolt_aura = aura if aura else "concentration"
        while (elapsed := (time.time() - start)) <= max_duration:
            cast_pos_abs = default_target_abs
            spray = default_spray
            atk_len = Config().char["atk_len_nihlathak"] * .50
            # if targets are detected, switch to targeting with reduced spread rather than present default cast position and default spread
            if target_detect and (targets := get_visible_blue_targets()):
                # log_targets(targets)
                spray = 5
                cast_pos_abs = targets[0].center_abs
                target_check_count += 1
                closest_target_position_monitor = targets[0].center_monitor



            # if time > minimum and either targets aren't set or targets don't exist, exit loop
            if elapsed > min_duration and (not target_detect or not targets):
                break

            targets = get_visible_blue_targets()
            if targets and len(targets) > 0:
                # TODO: add delay between FOH casts--doesn't properly cast each FOH in sequence
                # cast foh to holy bolt with preset ratio (e.g. 3 foh followed by 1 holy bolt if foh_to_holy_bolt_ratio = 3)
                    Logger.info("Mob detected, Attacking mobs!")
                    self.poison_nova(atk_len)
                    #self._raise_revive(cast_pos_abs, spray=spray)
                    self.corpse_explosion(cast_pos_abs, spray=spray) 
                    targets = get_visible_blue_targets()
                    if targets:
                        closest_target_position_monitor = targets[0].center_monitor
                        self.pre_move()
                        self.move(closest_target_position_monitor, force_move=True)
                    pos_m = screen.convert_abs_to_monitor((-50, 0))
                    self.walk(pos_m, force_move=True)
                    self.poison_nova(atk_len)                    
                    self._raise_revive(cast_pos_abs, spray=spray)
                    self._raise_mage(cast_pos_abs, spray=spray)
                    self._raise_skeleton(cast_pos_abs, spray=spray)
                    self.corpse_explosion(cast_pos_abs, spray=spray)

            else:
                    Logger.info("No minions detected yet, Default attack sequence")
                    targets = get_visible_blue_targets()
                    self.poison_nova(atk_len)
                    targets = get_visible_blue_targets()
                    self.corpse_explosion(cast_pos_abs, spray=spray)                    
                    self._raise_revive(cast_pos_abs, spray=spray)
                    self._raise_mage(cast_pos_abs, spray=spray)
                    self._raise_skeleton(cast_pos_abs, spray=spray)
                    self.corpse_explosion(cast_pos_abs, spray=spray)                   

            target_check_count += 1
        return True        

    def _attack_sequence(self, min_duration: float = Config().char["atk_len_cs_trashmobs"], max_duration: float = Config().char["atk_len_cs_trashmobs"] * 2):
        self._pn_attack_sequence(default_target_abs=(20,20), min_duration = min_duration, max_duration = max_duration, default_spray=10, blizz_to_ice_blast_ratio=2)

    def _trav_attack_sequence(self, min_duration: float = Config().char["atk_len_trav"], max_duration: float = Config().char["atk_len_trav"] * 4):
        self._trav_attack(default_target_abs=(20,20), min_duration = min_duration, max_duration = max_duration, default_spray=10, blizz_to_ice_blast_ratio=2)
            
    def _nihl_attack_sequence(self, min_duration: float = Config().char["atk_len_nihlathak"], max_duration: float = Config().char["atk_len_nihlathak"] * 4):
        self._nihl_attack(default_target_abs=(20,20), min_duration = min_duration, max_duration = max_duration, default_spray=10, blizz_to_ice_blast_ratio=2)
            
    def _pindle_attack_sequence(self, min_duration: float = Config().char["atk_len_nihlathak"], max_duration: float = Config().char["atk_len_nihlathak"] * 4):
        self._pindle_attack(default_target_abs=(20,20), min_duration = min_duration, max_duration = max_duration, default_spray=10, blizz_to_ice_blast_ratio=2)             

    def kill_pindle(self) -> bool:
        self.bone_armor()
        self._do_curse(.5)
        self._pindle_attack_sequence()
        self._pindle_attack_sequence()
        self._pindle_attack_sequence()
        # Move to items
        self._pather.traverse_nodes_fixed("pindle_end", self)
        return True

    def kill_eldritch(self) -> bool:
        pos_m = screen.convert_abs_to_monitor((0, -60))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self.bone_armor()
        self._do_curse(.5)
        self._attack_sequence()
        self._attack_sequence()
        # move a bit back
        self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, timeout=0.6, force_tp=True)
        return True


    def kill_shenk(self) -> bool:
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.0)
        pos_m = screen.convert_abs_to_monitor((50, 0))
        self.walk(pos_m, force_move=True)
        self._do_curse(.5)
        self._attack_sequence()
        self._attack_sequence()
        #self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=2,cast_v_div=1,cast_spell='corpse_explosion',delay=3.0,offset=1.8)
        return True


    def kill_council(self) -> bool:
        self.bone_armor()
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        atk_len = Config().char["atk_len_trav"]
        # Go inside and hammer a bit
        self._pather.traverse_nodes([228, 229], self, timeout=2.2, do_pre_move=False, force_tp=True, use_tp_charge=True)
        pos_m = screen.convert_abs_to_monitor((50, 50))
        self.walk(pos_m, force_move=True)
        # Move a bit back and another round
        self._do_curse(.5)
        self._trav_attack_sequence()
        self._pather.traverse_nodes([229], self, timeout=2.2, do_pre_move=False, force_tp=True, use_tp_charge=True)
        # Here we have two different attack sequences depending if tele is available or not
            # Back to center stairs and more hammers
            #self._pather.traverse_nodes([228], self, timeout=2.2, do_pre_move=False, force_tp=True, use_tp_charge=True)
        self._pather.traverse_nodes([300], self, timeout=2.2, do_pre_move=False, force_tp=True, use_tp_charge=True)
        pos_m = screen.convert_abs_to_monitor((50, -50))
        self.walk(pos_m, force_move=True)
        self._do_curse(.5)
        self._trav_attack_sequence()
        self._pather.traverse_nodes([300], self, timeout=2.2, do_pre_move=False, force_tp=True, use_tp_charge=True)
        #self._pather.traverse_nodes([228], self, timeout=2.2, do_pre_move=False, force_tp=True, use_tp_charge=True)
        self._pather.traverse_nodes([228], self, timeout=2.2, do_pre_move=False, force_tp=True, use_tp_charge=True)
        self._pather.traverse_nodes([226], self, timeout=2.2, do_pre_move=False, force_tp=True, use_tp_charge=True)
        pos_m = screen.convert_abs_to_monitor((50, -50))
        self.walk(pos_m, force_move=True)
        self._do_curse(.5)
        self._trav_attack_sequence()
            # move a bit to the top

        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        self.bone_armor()
        # Move close to nihlathak
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8, do_pre_move=True)
        self._do_curse(.5)
        self._nihl_attack_sequence()
        return True

    def kill_summoner(self) -> bool:
        # Attack
        pos_m = convert_abs_to_monitor((0, 20))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        # Attack
        self._do_curse(.5)
        self.poison_nova(Config().char["atk_len_arc"])
        # Move a bit back and another round
        return True


if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from char import Necro
    pather = Pather()
    char = Necro(Config().necro, Config().char, pather)
