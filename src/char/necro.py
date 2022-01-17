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
import cv2 #for Diablo
from item.pickit import PickIt #for Diablo


class Necro(IChar):
    def __init__(self, skill_hotkeys, char_config, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, pather: Pather, pickit: PickIt):
        Logger.info('\033[94m'+"Setting up Necro"+'\033[0m')
        super().__init__(skill_hotkeys, char_config, screen, template_finder, ui_manager)
        self._pickit = pickit #for Diablo
        self._picked_up_items = False #for Diablo
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
        if self._char_config["cta_available"]:
            self._pre_buff_cta()
        Logger.info("prebuff")


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


    def _clay_golem(self):
        Logger.info('\033[94m'+"cast ~> clay golem"+'\033[0m')
        keyboard.send(self._skill_hotkeys["clay_golem"])
        wait(0.05, 0.2)
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


    def _lower_resist(self, cast_pos_abs: Tuple[float, float], spray: float = 10):
        if self._skill_hotkeys["lower_resist"]:
            keyboard.send(self._skill_hotkeys["lower_resist"])
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


    def _poison_nova(self, duration: float): #, cast_pos_abs: Tuple[float, float], spray: float = 10):
        if self._skill_hotkeys["psn_nova"]:
            keyboard.send(self._skill_hotkeys["psn_nova"])
        #x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
        #y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
        #cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
        #mouse.move(*cast_pos_monitor)
        mouse.press(button="right")
        wait(duration, duration + 0.35)
        mouse.release(button="right")
        Logger.info('\x1b[1;32m'+"poison nova"+'\x1b[1;32m')


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
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=8,cast_v_div=2,cast_spell='raise_skeleton',offset=2,delay=1.6)
        wait(self._cast_duration, self._cast_duration +.2)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=4,cast_v_div=3,cast_spell='amp_dmg',delay=3.0)

        rot_deg=0       
        rot_deg=-180

        #enable this if your merc is dying
        pindle_pack_kill = bool(int(self._skill_hotkeys["clear_pindle_pack"]))

        if(pindle_pack_kill):
            Logger.info('\033[93m'+"optional pindle pack"+'\033[0m')
            if self._skill_hotkeys["psn_nova"]: self._poison_nova(1)
            self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=12,cast_v_div=2,cast_spell='corpse_explosion',delay=3.0,offset=1.8)
            wait(self._cast_duration, self._cast_duration +.2)
            self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=12,cast_v_div=2,cast_spell='corpse_explosion',delay=3.0,offset=1.8)
            wait(self._cast_duration, self._cast_duration +.1)
            self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=12,cast_v_div=2,cast_spell='raise_revive',delay=1.2,offset=1.8)

        #move to pindle combat position

        self._pather.traverse_nodes([102,103], self)
        if self._skill_hotkeys["psn_nova"]: self._poison_nova(1)

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
            if self._skill_hotkeys["psn_nova"]: self._poison_nova(1)
            self._left_attack_single(cast_pos_abs, 11, cast_count=8)
            if self._skill_hotkeys["psn_nova"]: self._poison_nova(1)
            rot_deg=0


            for _ in range(2):
                if self._skill_hotkeys["psn_nova"]: self._poison_nova(1)
                corpse_pos = unit_vector(rotate_vec(cast_pos_abs, rot_deg)) * 200
                self._corpse_explosion(pc,40,cast_count=2)
                rot_deg-=7
            rot_deg=0
            for _ in range(2):
                if self._skill_hotkeys["psn_nova"]: self._poison_nova(1)
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

    #-------------------------------------------------------------------------------#
    # Chaos Sanctuary, Seal Bosses (a = Vizier, b = De Seis, c = Infector) & Diablo #
    #-------------------------------------------------------------------------------#

    # GET TO PENTAGRAM
    def _loop_pentagram(self, path) -> bool:
        found = False

        templates = ["DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_2", "DIA_NEW_PENT_TP"]  #"DIA_NEW_PENT_3", "DIA_NEW_PENT_5 -> if these templates are found, you cannot calibrate at [602] #"DIA_NEW_PENT_6", 
        start_time = time.time()
        while not found and time.time() - start_time < 10:
            found = self._template_finder.search_and_wait(templates, threshold=0.83, time_out=0.1).valid
            if not found: self._pather.traverse_nodes_fixed(path, self)
        if not found:
            #if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/failed_loop_pentagram_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return False
        return True

    # OPEN SEALS
    def _sealdance(self, seal_opentemplates: list[str], seal_closedtemplates: list[str], seal_layout: str, seal_node: str) -> bool:
        i = 0
        while i < 6:
            # try to select seal
            Logger.debug(seal_layout + ": trying to open (try #" + str(i+1) + " of 7)")
            self.select_by_template(seal_closedtemplates, threshold=0.5, time_out=0.5)
            wait(i*0.5)
            # check if seal is opened
            found = self._template_finder.search_and_wait(seal_opentemplates, threshold=0.75, time_out=0.5, take_ss=False).valid
            if found:
                Logger.info(seal_layout + ": is open")
                break
            else:

                Logger.debug(seal_layout + ": not open")
                pos_m = self._screen.convert_abs_to_monitor((0, 0)) #remove mouse from seal
                mouse.move(*pos_m, randomize=[90, 160])
                wait(0.3)
                if i >= 2:
                    Logger.debug(seal_layout + ": failed " + str(i+2) + " of 7 times, trying to kill trash now") # ISSUE: if it failed 7/7 times, she does not try to open the seal: this way all the effort of the 7th try are useless. she should click at the end of the whole story. 
                    self.kill_cs_trash()
                    self._picked_up_items |= self._pickit.pick_up_items(self)
                    wait(i*0.5) #let the hammers clear & check the template -> the more tries, the longer the wait
                    if not self._pather.traverse_nodes(seal_node, self): return False # re-calibrate at seal node
                else:
                    # do a little random hop & try to click the seal
                    direction = 1 if i % 2 == 0 else -1
                    x_m, y_m = self._screen.convert_abs_to_monitor([50 * direction, direction]) #50 *  removed the Y component - we never want to end up BELOW the seal (any curse on our head will obscure the template check)
                    self.move((x_m, y_m), force_move=True)
                i += 1
        if self._config.general["info_screenshots"] and not found: cv2.imwrite(f"./info_screenshots/_failed_seal_{seal_layout}_{i}tries" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return found
        
    def kill_cs_trash_pentagram(self) -> bool:
        #FIGHT#
        return True

    def kill_cs_trash_seal(self, node:int) -> bool:
        if node == None:
            cast_pos_abs = 0, 0    
        cast_pos_abs = self._pather.find_abs_node_pos(node, self._screen.grab())
        pos_m = self._screen.convert_abs_to_monitor((1, -1))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self.bone_armor()
        self._lower_resist(cast_pos_abs, 11)
        wait(0.1, 0.2)
        self._poison_nova(1)
        wait(0.1, 0.2)
        self._raise_skeleton(cast_pos_abs,80,cast_count=4)
        self._revive(cast_pos_abs,80,cast_count=2)
        self._poison_nova(1)
        wait(0.1, 0.2)
        self._amp_dmg(cast_pos_abs, 11)
        corpse_exp_pos = cast_pos_abs
        self._corpse_explosion(corpse_exp_pos, 80, cast_count=4)
        self._raise_skeleton(cast_pos_abs,80,cast_count=4)
        self._revive(cast_pos_abs,80,cast_count=2)
        return True
    
    def kill_cs_trash(self) -> bool:
        cast_pos_abs = 0, 0    
        pos_m = self._screen.convert_abs_to_monitor((1, -1))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self.bone_armor()
        self._lower_resist(cast_pos_abs, 11)
        wait(0.1, 0.2)
        self._poison_nova(1)
        wait(0.1, 0.2)
        self._raise_skeleton(cast_pos_abs,80,cast_count=4)
        self._revive(cast_pos_abs,80,cast_count=2)
        self._poison_nova(1)
        wait(0.1, 0.2)
        self._amp_dmg(cast_pos_abs, 11)
        corpse_exp_pos = cast_pos_abs
        self._corpse_explosion(corpse_exp_pos, 80, cast_count=4)
        self._raise_skeleton(cast_pos_abs,80,cast_count=4)
        self._revive(cast_pos_abs,80,cast_count=2)
        return True
    
    def kill_vizier(self, seal_layout: str) -> bool: 
        #nodes1: list[int], nodes2: list[int]) -> bool:
        if seal_layout== "A1-L":
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            Logger.info(seal_layout +": Starting to clear Seal")
            ### CLEAR TRASH & APPROACH SEAL ###
            #self.kill_cs_trash() #done during sealcheck
            #self._picked_up_items |= self._pickit.pick_up_items(self) # not needed, we loot after vizier
            if not self._pather.traverse_nodes([611], self): return False
            if not self._pather.traverse_nodes([612, 613], self): return False
            self.kill_cs_trash()
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([614], self): return False
            if not self._sealdance(["DIA_A1L2_14_OPEN"], ["DIA_A1L2_14_CLOSED", "DIA_A1L2_14_CLOSED_DARK", "DIA_A1L2_14_MOUSEOVER"], seal_layout + "-Fake", [614]): return False
            if not self._pather.traverse_nodes([613, 615], self): return False
            if not self._sealdance(["DIA_A1L2_5_OPEN"], ["DIA_A1L2_5_CLOSED","DIA_A1L2_5_MOUSEOVER"], seal_layout + "-Boss", [615]): return False
            #if not self._pather.traverse_nodes([612], self): return False
            ### KILL BOSS ###
            Logger.info(seal_layout + ": Kill Boss A (Vizier)")
            #round1
            node_to = 612
            cast_pos_abs = self._pather.find_abs_node_pos(node_to, self._screen.grab())
            pos_m = self._screen.convert_abs_to_monitor((1, -1))
            self.pre_move()
            self.move(pos_m, force_move=True)
            self.bone_armor()
            self._lower_resist(cast_pos_abs, 11)
            wait(0.1, 0.2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._amp_dmg(cast_pos_abs, 11)
            corpse_exp_pos = cast_pos_abs
            self._corpse_explosion(corpse_exp_pos, 80, cast_count=4)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            # round2
            if not self._pather.traverse_nodes([612], self): return False
            node_to = 611
            cast_pos_abs = self._pather.find_abs_node_pos(node_to, self._screen.grab())
            pos_m = self._screen.convert_abs_to_monitor((1, -1))
            self.pre_move()
            self.move(pos_m, force_move=True)
            self.bone_armor()
            self._lower_resist(cast_pos_abs, 11)
            wait(0.1, 0.2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._amp_dmg(cast_pos_abs, 11)
            corpse_exp_pos = cast_pos_abs
            self._corpse_explosion(corpse_exp_pos, 80, cast_count=4)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            if not self._pather.traverse_nodes([612], self): return False
            ### LOOT ###
            #if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            #Logger.info(seal_layout + ": Hop!")
            if not self._pather.traverse_nodes([611], self): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            ### GO HOME ###
            if not self._pather.traverse_nodes([611], self): return False # calibrating here brings us home with higher consistency.
            Logger.info(seal_layout + ": Static Pathing to Pentagram")
            if not self._pather.traverse_nodes_fixed("dia_a1l_home", self): return False
            Logger.info(seal_layout + ": Looping to Pentagram")
            if not self._loop_pentagram("dia_a1l_home_loop"): return False
            if not self._pather.traverse_nodes([602], self, time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        elif seal_layout == "A2-Y":
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            Logger.info(seal_layout +": Starting to clear Seal")
            ### CLEAR TRASH & APPROACH SEAL ###
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.info(seal_layout + ": Hop!")
            if not self._pather.traverse_nodes([622], self): return False
            self.kill_cs_trash() #could be skipped to be faster, but helps clearing tempaltes at the calibration node 622 for returning home
            if not self._pather.traverse_nodes([623, 624], self): return False
            self.kill_cs_trash()
            if not self._pather.traverse_nodes([625], self): return False
            if not self._sealdance(["DIA_A2Y4_29_OPEN"], ["DIA_A2Y4_29_CLOSED", "DIA_A2Y4_29_MOUSEOVER"], seal_layout + "-Fake", [625]): return False
            self._pather.traverse_nodes_fixed("dia_a2y_sealfake_sealboss", self) #instead of traversing node 626 which causes issues
            if not self._sealdance(["DIA_A2Y4_36_OPEN"], ["DIA_A2Y4_36_CLOSED", "DIA_A2Y4_36_MOUSEOVER"], seal_layout + "-Boss", [626]): return False
            if not self._pather.traverse_nodes([627, 622], self): return False
            ### KILL BOSS ###
            #round 1
            Logger.info(seal_layout + ": Kill Boss A (Vizier)")
            node_to = 623
            cast_pos_abs = self._pather.find_abs_node_pos(node_to, self._screen.grab())
            pos_m = self._screen.convert_abs_to_monitor((1, -1))
            self.pre_move()
            self.move(pos_m, force_move=True)
            self.bone_armor()
            self._lower_resist(cast_pos_abs, 11)
            wait(0.1, 0.2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._amp_dmg(cast_pos_abs, 11)
            corpse_exp_pos = cast_pos_abs
            self._corpse_explosion(corpse_exp_pos, 80, cast_count=4)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            # round 2
            node_to = 623
            cast_pos_abs = self._pather.find_abs_node_pos(node_to, self._screen.grab())
            pos_m = self._screen.convert_abs_to_monitor((1, -1))
            self.pre_move()
            self.move(pos_m, force_move=True)
            self.bone_armor()
            self._lower_resist(cast_pos_abs, 11)
            wait(0.1, 0.2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._amp_dmg(cast_pos_abs, 11)
            corpse_exp_pos = cast_pos_abs
            self._corpse_explosion(corpse_exp_pos, 80, cast_count=4)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            ### LOOT ###
            #if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            #Logger.info(seal_layout + ": Hop!")
            if not self._pather.traverse_nodes([623], self): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            ### GO HOME ###
            if not self._pather.traverse_nodes([622], self): return False
            Logger.info(seal_layout + ": Looping to PENTAGRAM")
            if not self._loop_pentagram("dia_a2y_home_loop"): return False
            if not self._pather.traverse_nodes([602], self, time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        else: 
            Logger.debug("Variable Seal_Layout was " +seal_layout + ". Should not happen, aborting run")
            return False

    def kill_deseis(self, seal_layout: str) -> bool: 
        #nodes1: list[int], nodes2: list[int], nodes3: list[int]) -> bool:
        if seal_layout == "B1-S":
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            Logger.info(seal_layout +": Starting to clear Seal")
            ### CLEAR TRASH & APPROACH SEAL ###
            #self.kill_cs_trash() #done during sealcheck
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([634], self): return False
            self._sealdance(["DIA_B1S2_23_OPEN"], ["DIA_B1S2_23_CLOSED","DIA_B1S2_23_MOUSEOVER"], seal_layout + "-Boss", [634])
            ### KILL BOSS ###
            Logger.info(seal_layout + ": Kill Boss B (De Seis)")
            self._pather.traverse_nodes_fixed("dia_b1s_seal_deseis", self) # quite aggressive path, but has high possibility of directly killing De Seis with first hammers, for 50% of his spawn locations
            node_to = 631
            cast_pos_abs = self._pather.find_abs_node_pos(node_to, self._screen.grab())
            pos_m = self._screen.convert_abs_to_monitor((1, -1))
            self.pre_move()
            self.move(pos_m, force_move=True)
            self.bone_armor()
            self._lower_resist(cast_pos_abs, 11)
            wait(0.1, 0.2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._amp_dmg(cast_pos_abs, 11)
            corpse_exp_pos = cast_pos_abs
            self._corpse_explosion(corpse_exp_pos, 80, cast_count=4)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            ### GO HOME ###
            if not self._pather.traverse_nodes([633, 634], self): return False
            Logger.info(seal_layout + ": Static Pathing to Pentagram")
            self._pather.traverse_nodes_fixed("dia_b1s_home", self)
            Logger.info(seal_layout + ": Looping to PENTAGRAM")
            if not self._loop_pentagram("dia_b1s_home_loop"): return False
            if not self._pather.traverse_nodes([602], self , time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        elif seal_layout == "B2-U":
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            Logger.info(seal_layout +": Starting to clear Seal")
            ### CLEAR TRASH & APPROACH SEAL ###
            self._pather.traverse_nodes_fixed("dia_b2u_bold_seal", self)
            self._sealdance(["DIA_B2U2_16_OPEN"], ["DIA_B2U2_16_CLOSED", "DIA_B2U2_16_MOUSEOVER"], seal_layout + "-Boss", [644])
            ### KILL BOSS ###
            Logger.info(seal_layout + ": Kill Boss B (De Seis)")
            self._pather.traverse_nodes_fixed("dia_b2u_644_646", self) # We try to breaking line of sight, sometimes makes De Seis walk into the hammercloud. A better attack sequence here could make sense.
            node_to = 640
            pos_m = self._screen.convert_abs_to_monitor((1, -1))
            self.pre_move()
            self.move(pos_m, force_move=True)
            cast_pos_abs = self._pather.find_abs_node_pos(node_to, self._screen.grab())
            self.bone_armor()
            self._lower_resist(cast_pos_abs, 11)
            wait(0.1, 0.2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._amp_dmg(cast_pos_abs, 11)
            corpse_exp_pos = cast_pos_abs
            self._corpse_explosion(corpse_exp_pos, 80, cast_count=4)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([640], self): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            ### GO HOME ###
            if not self._pather.traverse_nodes([640], self): return False
            self._pather.traverse_nodes_fixed("dia_b2u_home", self)
            Logger.info(seal_layout + ": Static Pathing to Pentagram")
            Logger.info(seal_layout + ": Looping to PENTAGRAM")
            if not self._loop_pentagram("dia_b2u_home_loop"): return False
            if not self._pather.traverse_nodes([602], self , time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        else: 
            Logger.debug("Variable Seal_Layout was " +seal_layout + ". Should not happen, aborting run")
            return False

    def kill_infector(self, seal_layout: str) -> bool:
        if seal_layout == "C1-F":
            Logger.info(seal_layout +": Starting to clear Seal")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            ### CLEAR TRASH & APPROACH SEAL ###
            #self.kill_cs_trash() #done during layout check
            self._pather.traverse_nodes_fixed("dia_c1f_hop_fakeseal", self) # REPLACES: if not self._pather.traverse_nodes([656, 654, 655], self, time_out=3): return False #ISSUE: getting stuck on 704 often, reaching maxgamelength
            #self.kill_cs_trash()
            if not self._sealdance(["DIA_C1F_OPEN_NEAR"], ["DIA_C1F_CLOSED_NEAR","DIA_C1F_MOUSEOVER_NEAR"], seal_layout + "-Fake", [655]): return False #ISSUE: getting stuck on 705 during sealdance(), reaching maxgamelength
            self._pather.traverse_nodes_fixed("dia_c1f_654_651", self)
            if not self._sealdance(["DIA_C1F_BOSS_OPEN_RIGHT", "DIA_C1F_BOSS_OPEN_LEFT"], ["DIA_C1F_BOSS_MOUSEOVER_LEFT", "DIA_C1F_BOSS_CLOSED_NEAR_LEFT", "DIA_C1F_BOSS_CLOSED_NEAR_RIGHT"], seal_layout + "-Boss", [652]): return False
            self._pather.traverse_nodes_fixed("dia_c1f_652", self)
            ### KILL BOSS ###
            Logger.info(seal_layout + ": Kill Boss C (Infector)")
            node_to = 653
            cast_pos_abs = self._pather.find_abs_node_pos(node_to, self._screen.grab())
            pos_m = self._screen.convert_abs_to_monitor((1, -1))
            self.pre_move()
            self.move(pos_m, force_move=True)
            self.bone_armor()
            self._lower_resist(cast_pos_abs, 11)
            wait(0.1, 0.2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._amp_dmg(cast_pos_abs, 11)
            corpse_exp_pos = cast_pos_abs
            self._corpse_explosion(corpse_exp_pos, 80, cast_count=4)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            ### GO HOME ###
            if not self._pather.traverse_nodes([654], self, time_out=3): return False # this node often is not found
            Logger.info(seal_layout + ": Static Pathing to Pentagram")
            self._pather.traverse_nodes_fixed("dia_c1f_home", self)
            Logger.info(seal_layout + ": Looping to PENTAGRAM")
            if not self._loop_pentagram("dia_c1f_home_loop"): return False
            if not self._pather.traverse_nodes([602], self, time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        elif seal_layout == "C2-G":
            Logger.info(seal_layout +": Starting to clear Seal")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())            
            ### CLEAR TRASH & APPROACH SEAL ###
            if not self._pather.traverse_nodes([663, 662], self): return False
            if not self._sealdance(["DIA_C2G2_7_OPEN"], ["DIA_C2G2_7_CLOSED", "DIA_C2G2_7_MOUSEOVER"], seal_layout + "-Boss", [662]): return False
            self._pather.traverse_nodes_fixed("dia_c2g_663", self) # REPLACES for increased consistency: #if not self._pather.traverse_nodes([662, 663], self): return False
            Logger.info(seal_layout + ": Kill Boss C (Infector)")
            ### KILL BOSS ###
            node_to = 663
            cast_pos_abs = self._pather.find_abs_node_pos(node_to, self._screen.grab())
            pos_m = self._screen.convert_abs_to_monitor((1, -1))
            self.pre_move()
            self.move(pos_m, force_move=True)
            self.bone_armor()
            self._lower_resist(cast_pos_abs, 11)
            wait(0.1, 0.2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            self._poison_nova(1)
            wait(0.1, 0.2)
            self._amp_dmg(cast_pos_abs, 11)
            corpse_exp_pos = cast_pos_abs
            self._corpse_explosion(corpse_exp_pos, 80, cast_count=4)
            self._raise_skeleton(cast_pos_abs,80,cast_count=2)
            self._revive(cast_pos_abs,80,cast_count=2)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([664, 665], self): return False
            if not self._sealdance(["DIA_C2G2_21_OPEN"], ["DIA_C2G2_21_CLOSED", "DIA_C2G2_21_MOUSEOVER"], seal_layout + "-Fake", [665]): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            ### GO HOME ###
            if not self._pather.traverse_nodes([665], self): return False
            Logger.info(seal_layout + ": Static Pathing to Pentagram")
            self._pather.traverse_nodes_fixed("dia_c2g_home", self)
            Logger.info(seal_layout + ": Looping to PENTAGRAM")
            if not self._loop_pentagram("dia_c2g_home_loop"): return False
            if not self._pather.traverse_nodes([602], self, time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        else: 
            Logger.debug("Variable Seal_Layout was " +seal_layout + ". Should not happen, aborting run")
            return False

    def kill_diablo(self) -> bool:
        node_to = 602
        cast_pos_abs = self._pather.find_abs_node_pos(node_to, self._screen.grab())
        pos_m = self._screen.convert_abs_to_monitor((1, -1))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self.bone_armor()
        self._lower_resist(cast_pos_abs, 11)
        wait(0.1, 0.2)
        self._poison_nova(1)
        wait(0.1, 0.2)
        self._raise_skeleton(cast_pos_abs,80,cast_count=2)
        self._revive(cast_pos_abs,80,cast_count=2)
        self._poison_nova(1)
        wait(0.1, 0.2)
        self._amp_dmg(cast_pos_abs, 11)
        corpse_exp_pos = cast_pos_abs
        self._corpse_explosion(corpse_exp_pos, 80, cast_count=4)
        self._raise_skeleton(cast_pos_abs,80,cast_count=2)
        self._revive(cast_pos_abs,80,cast_count=2)

        self.pre_move()
        self.move(pos_m, force_move=True)
        self.bone_armor()
        self._lower_resist(cast_pos_abs, 11)
        wait(0.1, 0.2)
        self._poison_nova(1)
        wait(0.1, 0.2)
        self._poison_nova(1)
        wait(0.1, 0.2)
        self._amp_dmg(cast_pos_abs, 11)

        self.pre_move()
        self.move(pos_m, force_move=True)
        self.bone_armor()
        self._lower_resist(cast_pos_abs, 11)
        wait(0.1, 0.2)
        self._poison_nova(1)
        wait(0.1, 0.2)
        self._poison_nova(1)
        wait(0.1, 0.2)
        self._amp_dmg(cast_pos_abs, 11)


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
