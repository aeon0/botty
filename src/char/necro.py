import keyboard
from utils.custom_mouse import mouse
from char import IChar
from template_finder import TemplateFinder
from ui import UiManager
from pather import Pather
from logger import Logger
from screen import Screen
from utils.misc import wait, rotate_vec, unit_vector
import random
from typing import Tuple, Union, List
from pather import Location, Pather
import numpy as np
import time
from utils.misc import cut_roi, is_in_roi

class Necro(IChar):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, pather: Pather):
        Logger.info('\033[94m'+"Setting up Necro"+'\033[0m')
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager)
        self._pather = pather
        #custom necro pathing for pindle
        self._pather.adapt_path((Location.A5_PINDLE_START, Location.A5_PINDLE_SAFE_DIST), [100,101])
        self._pather.adapt_path((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), [104])
        #minor offsets to pindle fight locations
        self._pather.offset_node(102, [15, 0])
        self._pather.offset_node(103, [15, 0])
        self._pather.offset_node(101, [100,-5])
        #custom locations for shenk paths
        self._pather.adapt_path((Location.A5_SHENK_START, Location.A5_SHENK_SAFE_DIST),[141, 142, 143, 144, 145])
        self._pather.adapt_path((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), [149])
        #custom locations for trav paths
        self._pather.adapt_path((Location.A3_TRAV_START, Location.A3_TRAV_CENTER_STAIRS), [220, 221, 222, 223, 224, 225, 226])


    def _revive(self, cast_pos_abs: Tuple[float, float], spray: int = 10, cast_count: int=12):
        Logger.info('\033[94m'+"raise revive"+'\033[0m')
        keyboard.send(self._char_config["stand_still"], do_release=False)
        for _ in range(cast_count):
            if self._skill_hotkeys["raise_revive"]:
                keyboard.send(self._skill_hotkeys["raise_revive"])
                #Logger.info("revive -> cast")
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))

            nx = cast_pos_monitor[0]
            ny = cast_pos_monitor[1]
            if(nx>1280):
                nx=1275
            if(ny>720):
                ny=715
            if(nx<0):
                nx=0
            if(ny<0):
                ny=0
            clamp = [nx,ny]

            mouse.move(*clamp)
            mouse.press(button="right")
            wait(0.075, 0.1)
            mouse.release(button="right")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _raise_skeleton(self, cast_pos_abs: Tuple[float, float], spray: int = 10, cast_count: int=16):
        Logger.info('\033[94m'+"raise skeleton"+'\033[0m')
        keyboard.send(self._char_config["stand_still"], do_release=False)
        for _ in range(cast_count):
            if self._skill_hotkeys["raise_skeleton"]:
                keyboard.send(self._skill_hotkeys["raise_skeleton"])
                #Logger.info("raise skeleton -> cast")
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))

            nx = cast_pos_monitor[0]
            ny = cast_pos_monitor[1]
            if(nx>1280):
                nx=1279
            if(ny>720):
                ny=719
            if(nx<0):
                nx=0
            if(ny<0):
                ny=0
            clamp = [nx,ny]

            mouse.move(*clamp)
            mouse.press(button="right")
            wait(0.02, 0.05)
            mouse.release(button="right")
        keyboard.send(self._char_config["stand_still"], do_press=False)



    def pre_buff(self):
        # not used currently
        Logger.info("prebuff")

    def _clay_golem(self):
        Logger.info('\033[94m'+"cast ~> clay golem"+'\033[0m')
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



    def _left_attack(self, cast_pos_abs: Tuple[float, float], spray: int = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["skill_left"]:
            keyboard.send(self._skill_hotkeys["skill_left"])
        for _ in range(10):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(0.25, 0.3)
            mouse.release(button="left")

        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _left_attack_single(self, cast_pos_abs: Tuple[float, float], spray: int = 10, cast_count: int=6):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["skill_left"]:
            keyboard.send(self._skill_hotkeys["skill_left"])
        for _ in range(cast_count):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(0.25, 0.3)
            mouse.release(button="left")

        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _amp_dmg(self, cast_pos_abs: Tuple[float, float], spray: float = 10):
        if self._skill_hotkeys["amp_dmg"]:
            keyboard.send(self._skill_hotkeys["amp_dmg"])

        x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
        cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        mouse.press(button="right")
        wait(0.25, 0.35)
        mouse.release(button="right")

    def _corpse_explosion(self, cast_pos_abs: Tuple[float, float], spray: int = 10,cast_count: int = 8):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        Logger.info('\033[93m'+"corpse explosion~> random cast"+'\033[0m')
        for _ in range(cast_count):
            if self._skill_hotkeys["corpse_explosion"]:
                keyboard.send(self._skill_hotkeys["corpse_explosion"])
                x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
                y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
                cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
                mouse.move(*cast_pos_monitor)
                mouse.press(button="right")
                wait(0.075, 0.1)
                mouse.release(button="right")
        keyboard.send(self._char_config["stand_still"], do_press=False)


    def _lerp(self,a: float,b: float, f:float):
        return a + f * (b - a)

    def _cast_circle(self, cast_dir: Tuple[float,float],cast_start_angle: float=0.0, cast_end_angle: float=90.0,cast_div: int = 10,cast_v_div: int=4,cast_spell: str='raise_skeleton',delay: float=1.0,offset: float=1.0):
        Logger.info('\033[93m'+"circle cast ~>"+cast_spell+'\033[0m')
        keyboard.send(self._char_config["stand_still"], do_release=False)
        keyboard.send(self._skill_hotkeys[cast_spell])
        mouse.press(button="right")

        for i in range(cast_div):
            angle = self._lerp(cast_start_angle,cast_end_angle,float(i)/cast_div)
            target = unit_vector(rotate_vec(cast_dir, angle))
            #Logger.info("current angle ~> "+str(angle))
            for j in range(cast_v_div):
                circle_pos_screen = self._pather._adjust_abs_range_to_screen((target*120.0*float(j+1.0))*offset)
                circle_pos_monitor = self._screen.convert_abs_to_monitor(circle_pos_screen)
                mouse.move(*circle_pos_monitor,delay_factor=[0.3*delay, .6*delay])


                #Logger.info("circle move")
        mouse.release(button="right")
        keyboard.send(self._char_config["stand_still"], do_press=False)


    def kill_pindle(self) -> bool:

        atk_len = max(2, int(self._char_config["atk_len_pindle"] / 2))
        pindle_pos_abs = self._screen.convert_screen_to_abs(self._config.path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]

        pc = [pindle_pos_abs[0] * 0.9, (pindle_pos_abs[1]-50) * 0.9]


        raise_skel_pos = [0,10]
        rot_deg=0
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=32,cast_v_div=2,cast_spell='raise_skeleton',offset=2,delay=1.6)
        wait(self._cast_duration, self._cast_duration +.2)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=4,cast_v_div=3,cast_spell='amp_dmg',delay=3.0)

        rot_deg=0
        

        rot_deg=-180

        #enable this if your merc is dying
        pindle_pack_kill = bool(int(self._skill_hotkeys["clear_pindle_pack"]))

        if(pindle_pack_kill):
            Logger.info('\033[93m'+"optional pindle pack"+'\033[0m')
            self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=12,cast_v_div=2,cast_spell='corpse_explosion',delay=3.0,offset=1.8)
            wait(self._cast_duration, self._cast_duration +.2)
            self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=12,cast_v_div=2,cast_spell='corpse_explosion',delay=3.0,offset=1.8)
            wait(self._cast_duration, self._cast_duration +.1)
            self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=12,cast_v_div=2,cast_spell='raise_revive',delay=1.2,offset=1.8)

        #move to pindle combat position

        self._pather.traverse_nodes([102,103], self)


        wait(self._cast_duration, self._cast_duration +.2)

        # wiggle to unstick merc....
        pos_m = self._screen.convert_abs_to_monitor((0, -150))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(self._cast_duration, self._cast_duration +.1)
        self._bone_armor()

        # wiggle to unstick merc....
        pos_m = self._screen.convert_abs_to_monitor((0, 150))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(self._cast_duration, self._cast_duration +.1)

        self._amp_dmg(cast_pos_abs, 11)
        wait(self._cast_duration, self._cast_duration +.2)
        self._clay_golem()

        
        for _ in range(atk_len):
            Logger.info('\033[96m'+ "pindle atk cycle" + '\033[0m')
            self._amp_dmg(cast_pos_abs, 11)
            self._left_attack_single(cast_pos_abs, 11, cast_count=8)
            rot_deg=0


            for _ in range(2):
                corpse_pos = unit_vector(rotate_vec(cast_pos_abs, rot_deg)) * 200
                self._corpse_explosion(pc,40,cast_count=2)
                rot_deg-=7
            rot_deg=0
            for _ in range(2):
                corpse_pos = unit_vector(rotate_vec(cast_pos_abs, rot_deg)) * 200
                self._corpse_explosion(pc,40,cast_count=2)
                rot_deg+=7

            # wiggle to unstick merc
            pos_m = self._screen.convert_abs_to_monitor((0, -150))
            self.pre_move()
            self.move(pos_m, force_move=True)            
            wait(self._cast_duration, self._cast_duration +.1)
            pos_m = self._screen.convert_abs_to_monitor((0, 150))
            self.pre_move()
            self.move(pos_m, force_move=True)
            wait(self._cast_duration, self._cast_duration +.1)

        self._revive(cast_pos_abs,50,cast_count=4)

        Logger.info('\033[92m'+"atk cycle end"+'\033[0m')
        #wait for pindle to die just incase - maybe needs death detection
        wait(self._cast_duration, self._cast_duration + 0.4)
        if self.can_teleport():
            self._pather.traverse_nodes("pindle_end", self)
        else:
            self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, force_tp=True)
        return True

    def kill_eldritch(self) -> bool:
        atk_len = max(2, int(self._char_config["atk_len_eldritch"] / 2))
        eld_pos_abs = self._screen.convert_screen_to_abs(self._config.path["eldritch_end"][0])
        cast_pos_abs = [eld_pos_abs[0] * 0.9, eld_pos_abs[1] * 0.9]


        self.bone_armor()
        
        # move a bit back
        pos_m = self._screen.convert_abs_to_monitor((0, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)

        self._amp_dmg(cast_pos_abs, 11)
        corpse_exp_pos = [0,-80]

        for _ in range(atk_len):
            #Logger.info("atk cycle")
            Logger.info('\033[96m'+ "eldrich atk cycle" + '\033[0m')
            self._left_attack_single(cast_pos_abs, 11, cast_count=8)
            self._corpse_explosion(cast_pos_abs, 60, cast_count=4)
        Logger.info('\033[92m'+"atk cycle end"+'\033[0m')

        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        if self.can_teleport():
            self._pather.traverse_nodes_fixed("eldritch_end", self)
        else:
            self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, time_out=0.6, force_tp=True)
        self.bone_armor()

        #get some more summons out for elite packs
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=12,cast_v_div=4,cast_spell='raise_revive',delay=1.2,offset=.8)
        self._raise_skeleton([0,-40],80,cast_count=4)

        # move a bit back
        pos_m = self._screen.convert_abs_to_monitor((0, -350))
        self.pre_move()
        self.move(pos_m, force_move=True)


        return True


    def kill_shenk(self) -> bool:
        #stop to kill potentially troublesome packs
        Logger.info('\033[93m'+"dealing with posible packs"+'\033[0m')

        self.bone_armor()
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=4,cast_v_div=3,cast_spell='amp_dmg',delay=3.0)
        self._corpse_explosion([0,50], 80, cast_count=8)

        #continue to shenk fight
        self._pather.traverse_nodes(([ 146, 147, 148]), self, time_out=1.4, force_tp=True)

        shenk_pos_abs = self._pather.find_abs_node_pos(149, self._screen.grab())
        if shenk_pos_abs is None:
            shenk_pos_abs = self._screen.convert_screen_to_abs(self._config.path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        self.bone_armor()

        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=4,cast_v_div=3,cast_spell='amp_dmg',delay=3.0)
        corpse_exp_pos = [200,80]

        for _ in range(int(self._char_config["atk_len_shenk"])):
            Logger.info('\033[96m'+ "shenk atk cycle" + '\033[0m')
            self._left_attack_single(cast_pos_abs, 11, cast_count=4)
            self._bone_armor()
            self._amp_dmg(cast_pos_abs, 11)
            self._corpse_explosion(corpse_exp_pos, 80, cast_count=12)
        Logger.info('\033[92m'+"atk cycle end"+'\033[0m')

        self._raise_skeleton(cast_pos_abs,80,cast_count=4)
        self._revive(cast_pos_abs,80,cast_count=4)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes(([148,149]), self, time_out=3.4, force_tp=True)
        return True

    def kill_council(self) -> bool:

  
        #this could still use some work, mostly works though, needs a fairly well geared merc

        self._bone_armor()
        wait(self._cast_duration, self._cast_duration +.4)
        self._clay_golem()




        cast_pos_abs = [-300,-200]



        corpse_exp_pos = cast_pos_abs

        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        atk_len = self._char_config["atk_len_trav"]
        # Go inside and hammer a bit
        self.bone_armor()
        self._left_attack_single(cast_pos_abs, 11, cast_count=4)
        self._amp_dmg(cast_pos_abs, 11)
        self._corpse_explosion(corpse_exp_pos, 80, cast_count=8)

         # wiggle to unstick merc....
        pos_m = self._screen.convert_abs_to_monitor((0, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(self._cast_duration, self._cast_duration +.1)
        

        # wiggle to unstick merc....
        pos_m = self._screen.convert_abs_to_monitor((0, -50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(self._cast_duration, self._cast_duration +.1)
    
        wait(self._cast_duration, self._cast_duration +.1)
        self._bone_armor()
        self._left_attack_single(cast_pos_abs, 11, cast_count=4)
    
        self._corpse_explosion(corpse_exp_pos, 80, cast_count=12)


        # wiggle to unstick merc....
        pos_m = self._screen.convert_abs_to_monitor((0, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(self._cast_duration, self._cast_duration +.1)
    
        # wiggle to unstick merc....
        pos_m = self._screen.convert_abs_to_monitor((0, -50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(self._cast_duration, self._cast_duration +.1)
        cast_pos_abs = [50,-50]

        self._amp_dmg(cast_pos_abs, 11)
        self._bone_armor()
        self._left_attack_single(cast_pos_abs, 11, cast_count=4)
        self._corpse_explosion(corpse_exp_pos, 80, cast_count=8)
        self._bone_armor()
        self._left_attack_single(cast_pos_abs, 11, cast_count=4)
        self._corpse_explosion(corpse_exp_pos, 240, cast_count=18)


        #take care of inside mobs
        self._pather.offset_node(229, [250, 130])
        self._pather.traverse_nodes([228, 229], self, time_out=2.5, force_tp=True)
        self._pather.offset_node(229, [-250, -130])
        atk_pos_abs = self._pather.find_abs_node_pos(230, self._screen.grab())
        if atk_pos_abs is None:
            Logger.debug("Could not find node [230]. Using static attack coordinates instead.")
            atk_pos_abs = [-300, -200]
        else:
            atk_pos_abs = [atk_pos_abs[0], atk_pos_abs[1] + 70]
        cast_pos_abs = np.array([atk_pos_abs[0] * 0.9, atk_pos_abs[1] * 0.9])

        self.bone_armor()
        self._left_attack_single(cast_pos_abs, 11, cast_count=4)
        self._amp_dmg(cast_pos_abs, 11)
        self._corpse_explosion(corpse_exp_pos, 80, cast_count=8)

         # wiggle to unstick merc....
        pos_m = self._screen.convert_abs_to_monitor((0, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(self._cast_duration, self._cast_duration +.1)
        

        # wiggle to unstick merc....
        pos_m = self._screen.convert_abs_to_monitor((0, -50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(self._cast_duration, self._cast_duration +.1)
    
        wait(self._cast_duration, self._cast_duration +.1)
        self._bone_armor()
        self._left_attack_single(cast_pos_abs, 11, cast_count=4)
    
        self._corpse_explosion(corpse_exp_pos, 80, cast_count=12)


        # wiggle to unstick merc....
        pos_m = self._screen.convert_abs_to_monitor((0, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(self._cast_duration, self._cast_duration +.1)
    
        # wiggle to unstick merc....
        pos_m = self._screen.convert_abs_to_monitor((0, -50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(self._cast_duration, self._cast_duration +.1)
        #cast_pos_abs = [-300,-200]

        self._amp_dmg(cast_pos_abs, 11)
        self._bone_armor()
        self._left_attack_single(cast_pos_abs, 11, cast_count=4)
        self._corpse_explosion(corpse_exp_pos, 80, cast_count=8)
        self._bone_armor()
        self._left_attack_single(cast_pos_abs, 11, cast_count=4)
        self._corpse_explosion(corpse_exp_pos, 240, cast_count=18)
        

        self._pather.traverse_nodes([230, 229 ,228], self, time_out=2.5, force_tp=True)
        Logger.info('\033[92m'+"atk cycle end"+'\033[0m')


        return True


if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from char import Necro
    from ui import UiManager
    config = Config()
    screen = Screen(config.general["monitor"])
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
    char = Necro(config.necro, config.char, screen, t_finder, ui_manager, pather)
