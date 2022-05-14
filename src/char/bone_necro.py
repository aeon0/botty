import keyboard
from utils.custom_mouse import mouse
from char import IChar
import template_finder
from pather import Pather
from logger import Logger
from screen import grab, convert_abs_to_monitor, convert_screen_to_abs
from config import Config
from utils.misc import wait, rotate_vec, unit_vector
import random
from typing import Tuple
from pather import Location, Pather
import screen as screen
import numpy as np
import time
import os
from ui_manager import ScreenObjects

class Bone_Necro(IChar):
    def __init__(self, skill_hotkeys: dict, pather: Pather):
        Logger.info("Setting up Bone Necro")
        super().__init__(skill_hotkeys)
        self._pather = pather
        if "damage_scaling" in Config().bone_necro:
            self.damage_scaling = float(Config().bone_necro["damage_scaling"])
            
    def move_to(self, x, y):
        pos_m = convert_abs_to_monitor((x, y))
        self.pre_move()
        self.move(pos_m, force_move=True)
    
    def bone_wall(self, cast_pos_abs: Tuple[float, float], spray: int):
        if not self._skill_hotkeys["bone_wall"]:
            raise ValueError("You did not set bone_wall hotkey!")
        keyboard.send(Config().char["stand_still"], do_release=False)
        keyboard.send(self._skill_hotkeys["bone_wall"])
        wait(0.02, 0.08)
        x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        mouse.press(button="right")
        wait(self._cast_duration+.04, self._cast_duration+.08)
        mouse.release(button="right")
        keyboard.send(Config().char["stand_still"], do_press=False)    

    def pre_buff(self):
        self.bone_armor()
        #only CTA if pre trav
        if Config().char["cta_available"]:
            self._pre_buff_cta()
        Logger.info("prebuff/cta")

    def _clay_golem(self):
        Logger.debug('Casting clay golem')
        keyboard.send(self._skill_hotkeys["clay_golem"])
        wait(0.05, 0.2)
        mouse.click(button="right")
        wait(self._cast_duration)

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

    def _corpse_explosion(self, cast_pos_abs: Tuple[float, float], spray: int = 10,cast_count: int = 8):
        keyboard.send(Config().char["stand_still"], do_release=False)
        Logger.debug(f'casting corpse explosion {cast_count} times with spray = {spray}')
        for _ in range(cast_count):
            if self._skill_hotkeys["corpse_explosion"]:
                keyboard.send(self._skill_hotkeys["corpse_explosion"])
                x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
                y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
                cast_pos_monitor = convert_abs_to_monitor((x, y))
                mouse.move(*cast_pos_monitor)
                mouse.press(button="right")
                wait(0.075, 0.1)
                mouse.release(button="right")
        keyboard.send(Config().char["stand_still"], do_press=False)


    def _lerp(self,a: float,b: float, f:float):
        return a + f * (b - a)

    def _cast_circle(self, cast_dir: Tuple[float,float],cast_start_angle: float=0.0, cast_end_angle: float=90.0,cast_div: int = 10,cast_spell: str='raise_skeleton',delay: float=1.0, radius=120, hold_duration: float = 3, hold=True):
        if hold:
            Logger.info(f'Circle cast {cast_spell} from {cast_start_angle}º to {cast_end_angle}º over {hold_duration}s')
        else:
            Logger.info(f'Circle cast {cast_spell} from {cast_start_angle}º to {cast_end_angle}º over {cast_div} casts')
        
        keyboard.send(Config().char["stand_still"], do_release=False)
        keyboard.send(self._skill_hotkeys[cast_spell])
        if hold:
            mouse.press(button="right")

        for i in range(cast_div):
            angle = self._lerp(cast_start_angle,cast_end_angle,float(i)/cast_div)
            target = unit_vector(rotate_vec(cast_dir, angle))
            Logger.debug(f"Circle cast - current angle: {angle}º")
            circle_pos_screen = self._pather._adjust_abs_range_to_screen(target*radius)
            circle_pos_monitor = convert_abs_to_monitor(circle_pos_screen)
            start = time.time()
            mouse.move(*circle_pos_monitor,delay_factor=[0.95*delay, 1.05*delay])
            duration = time.time() - start

            if not hold:
                mouse.press(button="right")
                wait(.04, .08)
                mouse.release(button="right")
                wait(self._cast_duration)
            else:
                #adjust the speed so we finish in approximately the time requested
                expected = (hold_duration/cast_div)
                delay = delay*(expected/duration)
        if hold:
            mouse.release(button="right")
        keyboard.send(Config().char["stand_still"], do_press=False)


    def kill_pindle(self) -> bool:
        for pos in [[200,-100], [-150,100] ]:
            self.bone_wall(pos, spray=10)
        self.cast_in_arc(ability='bone_spear', cast_pos_abs=[110,-50], spread_deg=15, time_in_s=5)
        self._corpse_explosion([165,-75], spray=100, cast_count=5)
        self.cast_in_arc(ability='bone_spirit', cast_pos_abs=[110,-50], spread_deg=15, time_in_s=2.5)
        self._pather.traverse_nodes_fixed("pindle_end", self)
        return True

    def kill_eldritch(self) -> bool:
        #build an arc of bone walls
        for pos in [[50,-200], [-200,-175], [-350,50]]:
            self.bone_wall(pos, spray=10)
        self.cast_in_arc(ability='teeth', cast_pos_abs=[-20,-150], spread_deg=15, time_in_s=3)
        self.cast_in_arc(ability='bone_spear', cast_pos_abs=[-20,-150], spread_deg=15, time_in_s=2)
        self._corpse_explosion([-20,-240], spray=100, cast_count=5)
        self.cast_in_arc(ability='bone_spirit', cast_pos_abs=[0,-80], spread_deg=60, time_in_s=2.5)
        self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, timeout=0.6, force_tp=True)
        self.bone_armor()
        return True


    def kill_shenk(self) -> bool:
        self._cast_circle(cast_dir=[1,1],cast_start_angle=0,cast_end_angle=360,cast_div=5,cast_spell='bone_wall',delay=.8,radius=100, hold=False)
        self.cast_in_arc(ability='teeth', cast_pos_abs=[160,75], spread_deg=360, time_in_s=6)
        self.cast_in_arc(ability='teeth', cast_pos_abs=[160,75], spread_deg=30, time_in_s=2)
        self._corpse_explosion([0,0], spray=200, cast_count=4)
        self.cast_in_arc(ability='bone_spear', cast_pos_abs=[160,75], spread_deg=30, time_in_s=3)
        self._corpse_explosion([240,112], spray=200, cast_count=8)
        self.cast_in_arc(ability='bone_spirit', cast_pos_abs=[80,37], spread_deg=60, time_in_s=3)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.0)
        return True


    def kill_council(self) -> bool:
        #move down adjacent to the right moat
        self.move_to(-150,150)
        self.move_to(-150,150)
 
        #moat on right side, encircle with bone walls on the other 3 sides
        for pos in [[100,-100], [-125,-25], [-50,100]]:
            self.bone_wall(pos, spray=10)
        self.cast_in_arc(ability='teeth', cast_pos_abs=[40,-100], spread_deg=180, time_in_s=5)
        self.cast_in_arc(ability='bone_spear', cast_pos_abs=[40,-100], spread_deg=120, time_in_s=8)
        
        self._corpse_explosion([40,-100], spray=200, cast_count=8)
        self.cast_in_arc(ability='bone_spirit', cast_pos_abs=[20,-50], spread_deg=180, time_in_s=5)
        self._corpse_explosion([40,-100], spray=200, cast_count=8)
        self.cast_in_arc(ability='bone_spirit', cast_pos_abs=[20,-50], spread_deg=360, time_in_s=4)
        
        return True


    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        nihlathak_pos_abs = self._pather.find_abs_node_pos(end_nodes[-1], grab())
        if nihlathak_pos_abs is None:
            return False
            
        cast_pos_abs = np.array(nihlathak_pos_abs)*.2
        self._cast_circle(cast_dir=[1,1],cast_start_angle=0,cast_end_angle=360,cast_div=5,cast_spell='bone_wall',delay=.8,radius=100, hold=False)
        self._bone_armor()
        self.cast_in_arc(ability='teeth', cast_pos_abs=cast_pos_abs, spread_deg=150, time_in_s=5)
        self._bone_armor()
        self._corpse_explosion(cast_pos_abs, spray=200, cast_count=8)
        self.cast_in_arc(ability='bone_spear', cast_pos_abs=cast_pos_abs, spread_deg=10, time_in_s=5)
        self._bone_armor()

        self._corpse_explosion(np.array(nihlathak_pos_abs)*.75, spray=200, cast_count=10)
        self.cast_in_arc(ability='bone_spirit', cast_pos_abs=cast_pos_abs, spread_deg=30, time_in_s=2.5)

        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8)
        return True

    def kill_summoner(self) -> bool:
        # Attack
        self.cast_in_arc(ability='teeth', cast_pos_abs=[30,30], spread_deg=360, time_in_s=3)
        self.cast_in_arc(ability='bone_spirit', cast_pos_abs=[30,30], spread_deg=360, time_in_s=2)
        self._corpse_explosion([0,0], spray=200, cast_count=8)
        self.cast_in_arc(ability='bone_spirit', cast_pos_abs=[30,30], spread_deg=360, time_in_s=2)
            
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
