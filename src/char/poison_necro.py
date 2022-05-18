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


    def _check_shenk_death(self):
        ''' make sure shenk is dead checking for fireballs so we can exit combat sooner '''

        roi = [640,0,640,720]
        img = grab()

        template_match = template_finder.search(
            ['SHENK_DEATH_1','SHENK_DEATH_2','SHENK_DEATH_3','SHENK_DEATH_4'],
            img,
            threshold=0.6,
            roi=roi,
            use_grayscale = False
        )
        if template_match.valid:
            self._shenk_dead=1
            Logger.info('\33[31m'+"Shenks Dead, looting..."+'\033[0m')
        else:
            return True

    def _count_revives(self):
        roi = [15,14,400,45]
        img = grab()
        max_rev = 13

        template_match = template_finder.search(
            ['REV_BASE'],
            img,
            threshold=0.6,
            roi=roi
        )
        if template_match.valid:
            self._revive_count=max_rev
        else:
            self._revive_count=0
            return True

        for count in range(1,max_rev):
            rev_num = "REV_"+str(count)
            template_match = template_finder.search(
                [rev_num],
                img,
                threshold=0.66,
                roi=roi,
                use_grayscale = False
            )
            if template_match.valid:
                self._revive_count=count


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

    def _count_skeletons(self):
        roi = [15,14,400,45]
        img = grab()
        max_skeles = 13

        template_match = template_finder.search(
            ['SKELE_BASE'],
            img,
            threshold=0.6,
            roi=roi
        )
        if template_match.valid:
            self._skeletons_count=max_skeles
        else:
            self._skeletons_count=0
            return True

        for count in range(1,max_skeles):
            skele_num = "SKELE_"+str(count)
            template_match = template_finder.search(
                [skele_num],
                img,
                threshold=0.66,
                roi=roi,
                use_grayscale = False
            )
            if template_match.valid:
                self._skeletons_count=count

    def _count_gol(self):
        roi = [15,14,400,45]
        img = grab()

        template_match = template_finder.search(
            ['CLAY'],
            img,
            threshold=0.6,
            roi=roi
        )
        if template_match.valid:
            self._golem_count="clay gol"
        else:
            self._golem_count="none"
            return True

    def _summon_count(self):
        ''' see how many summons and which golem are out '''

        self._count_skeletons()
        self._count_revives()
        self._count_gol()
    def _summon_stat(self):
        ''' print counts for summons '''
        Logger.info('\33[31m'+"Summon status | "+str(self._skeletons_count)+"skele | "+str(self._revive_count)+" rev | "+self._golem_count+" |"+'\033[0m')

    def _revive(self, cast_pos_abs: Tuple[float, float], spray: int = 10, cast_count: int=12):
        Logger.info('\033[94m'+"raise revive"+'\033[0m')
        keyboard.send(Config().char["stand_still"], do_release=False)
        for _ in range(cast_count):
            if self._skill_hotkeys["raise_revive"]:
                keyboard.send(self._skill_hotkeys["raise_revive"])
                #Logger.info("revive -> cast")
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = screen.convert_abs_to_monitor((x, y))

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
        keyboard.send(Config().char["stand_still"], do_press=False)

    def _raise_skeleton(self, cast_pos_abs: Tuple[float, float], spray: int = 10, cast_count: int=16):
        Logger.info('\033[94m'+"raise skeleton"+'\033[0m')
        keyboard.send(Config().char["stand_still"], do_release=False)
        for _ in range(cast_count):
            if self._skill_hotkeys["raise_skeleton"]:
                keyboard.send(self._skill_hotkeys["raise_skeleton"])
                #Logger.info("raise skeleton -> cast")
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = screen.convert_abs_to_monitor((x, y))

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
        keyboard.send(Config().char["stand_still"], do_press=False)

    def _raise_mage(self, cast_pos_abs: Tuple[float, float], spray: int = 10, cast_count: int=16):
        Logger.info('\033[94m'+"raise mage"+'\033[0m')
        keyboard.send(Config().char["stand_still"], do_release=False)
        for _ in range(cast_count):
            if self._skill_hotkeys["raise_mage"]:
                keyboard.send(self._skill_hotkeys["raise_mage"])
                #Logger.info("raise skeleton -> cast")
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = screen.convert_abs_to_monitor((x, y))

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
        keyboard.send(Config().char["stand_still"], do_press=False)


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

    def _left_attack_single(self, cast_pos_abs: Tuple[float, float], spray: int = 10, cast_count: int=6):
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

    def _amp_dmg(self, cast_pos_abs: Tuple[float, float], spray: float = 10):
        if self._skill_hotkeys["amp_dmg"]:
            keyboard.send(self._skill_hotkeys["amp_dmg"])

        x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
        cast_pos_monitor = screen.convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        mouse.press(button="right")
        wait(0.25, 0.35)
        mouse.release(button="right")

    def _lower_res(self, cast_pos_abs: Tuple[float, float], spray: float = 10):
        if self._skill_hotkeys["lower_res"]:
            keyboard.send(self._skill_hotkeys["lower_res"])

        x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
        cast_pos_monitor = screen.convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        mouse.press(button="right")
        wait(0.25, 0.35)
        mouse.release(button="right")        

    def _corpse_explosion(self, cast_pos_abs: Tuple[float, float], spray: int = 10,cast_count: int = 8):
        keyboard.send(Config().char["stand_still"], do_release=False)
        Logger.info('\033[93m'+"corpse explosion~> random cast"+'\033[0m')
        for _ in range(cast_count):
            if self._skill_hotkeys["corpse_explosion"]:
                keyboard.send(self._skill_hotkeys["corpse_explosion"])
                x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
                y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
                cast_pos_monitor = screen.convert_abs_to_monitor((x, y))
                mouse.move(*cast_pos_monitor)
                mouse.press(button="right")
                wait(0.075, 0.1)
                mouse.release(button="right")
        keyboard.send(Config().char["stand_still"], do_press=False)


    def _lerp(self,a: float,b: float, f:float):
        return a + f * (b - a)

    def _cast_circle(self, cast_dir: Tuple[float,float],cast_start_angle: float=0.0, cast_end_angle: float=90.0,cast_div: int = 10,cast_v_div: int=4,cast_spell: str='raise_skeleton',delay: float=1.0,offset: float=1.0):
        Logger.info('\033[93m'+"circle cast ~>"+cast_spell+'\033[0m')
        keyboard.send(Config().char["stand_still"], do_release=False)
        keyboard.send(self._skill_hotkeys[cast_spell])
        mouse.press(button="right")

        for i in range(cast_div):
            angle = self._lerp(cast_start_angle,cast_end_angle,float(i)/cast_div)
            target = unit_vector(rotate_vec(cast_dir, angle))
            #Logger.info("current angle ~> "+str(angle))
            for j in range(cast_v_div):
                circle_pos_screen = self._pather._adjust_abs_range_to_screen((target*120.0*float(j+1.0))*offset)
                circle_pos_monitor = screen.convert_abs_to_monitor(circle_pos_screen)
                mouse.move(*circle_pos_monitor,delay_factor=[0.3*delay, .6*delay])


                #Logger.info("circle move")
        mouse.release(button="right")
        keyboard.send(Config().char["stand_still"], do_press=False)


    def kill_pindle(self) -> bool:
        pos_m = screen.convert_abs_to_monitor((0, 30))
        self.walk(pos_m, force_move=True)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=4,cast_v_div=3,cast_spell='lower_res',delay=1.0)
        self.poison_nova(3.0)
        pos_m = screen.convert_abs_to_monitor((0, -50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        pos_m = screen.convert_abs_to_monitor((50, 0))
        self.walk(pos_m, force_move=True)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=120,cast_div=5,cast_v_div=2,cast_spell='corpse_explosion',delay=1.1,offset=1.8)
        self.poison_nova(3.0)
        return True

    def kill_eldritch(self) -> bool:
        pos_m = screen.convert_abs_to_monitor((0, -100))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self.bone_armor()
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=4,cast_v_div=3,cast_spell='lower_res',delay=1.0)
        self.poison_nova(2.0)
        self._summon_stat()
        # move a bit back
        pos_m = screen.convert_abs_to_monitor((0, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self.poison_nova(2.0)
        self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, timeout=0.6, force_tp=True)
        pos_m = screen.convert_abs_to_monitor((0, 170))
        self.pre_move()
        self.move(pos_m, force_move=True)
        #self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=8,cast_v_div=4,cast_spell='raise_revive',delay=1.2,offset=.8)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=720,cast_div=8,cast_v_div=4,cast_spell='raise_skeleton',delay=1.1,offset=.8)
        pos_m = screen.convert_abs_to_monitor((0, -50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=720,cast_div=8,cast_v_div=4,cast_spell='raise_mage',delay=1.1,offset=1.0)
        pos_m = screen.convert_abs_to_monitor((-75, 0))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=720,cast_div=8,cast_v_div=4,cast_spell='raise_skeleton',delay=1.1,offset=.5)
        self._summon_count()
        self._summon_stat()

        self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, timeout=0.6, force_tp=True)
        return True


    def kill_shenk(self) -> bool:
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.0)
        #pos_m = self._screen.convert_abs_to_monitor((50, 0))
        #self.walk(pos_m, force_move=True)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=4,cast_v_div=3,cast_spell='lower_res',delay=1.0)
        self.poison_nova(3.0)
        pos_m = screen.convert_abs_to_monitor((0, -50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=720,cast_div=10,cast_v_div=4,cast_spell='raise_mage',delay=1.1,offset=.8)
        pos_m = screen.convert_abs_to_monitor((50, 0))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=720,cast_div=10,cast_v_div=4,cast_spell='raise_revive',delay=1.1,offset=.8)
        pos_m = screen.convert_abs_to_monitor((-20, -20))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=10,cast_v_div=4,cast_spell='raise_skeleton',delay=1.1,offset=.8)
        self._summon_count()
        #self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=2,cast_v_div=1,cast_spell='corpse_explosion',delay=3.0,offset=1.8)
        return True


    def kill_council(self) -> bool:
        pos_m = screen.convert_abs_to_monitor((0, -200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._pather.traverse_nodes([229], self, timeout=2.5, force_tp=True, use_tp_charge=True)       
        pos_m = screen.convert_abs_to_monitor((50, 0))
        self.walk(pos_m, force_move=True)
        #self._lower_res((-50, 0), spray=10)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=4,cast_v_div=3,cast_spell='lower_res',delay=1.0)  
        self.poison_nova(2.0)
        #self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=9,cast_v_div=3,cast_spell='raise_skeleton',delay=1.2,offset=.8)
        pos_m = screen.convert_abs_to_monitor((200, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        pos_m = screen.convert_abs_to_monitor((30, -50))
        self.walk(pos_m, force_move=True)
        self.poison_nova(2.0)
        #self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=120,cast_div=2,cast_v_div=1,cast_spell='corpse_explosion',delay=3.0,offset=1.8)
        #wait(self._cast_duration, self._cast_duration +.2)
        pos_m = screen.convert_abs_to_monitor((-200, 200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        pos_m = screen.convert_abs_to_monitor((-100, 200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._pather.traverse_nodes([226], self, timeout=2.5, force_tp=True, use_tp_charge=True)
        pos_m = screen.convert_abs_to_monitor((0, 30))
        self.walk(pos_m, force_move=True)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=4,cast_v_div=3,cast_spell='lower_res',delay=1.0)
        wait(0.5)
        self.poison_nova(4.0)
        #self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=120,cast_div=2,cast_v_div=1,cast_spell='corpse_explosion',delay=3.0,offset=1.8)
        #wait(self._cast_duration, self._cast_duration +.2)
        #self.poison_nova(2.0)
        pos_m = screen.convert_abs_to_monitor((50, 0))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=120,cast_div=5,cast_v_div=2,cast_spell='corpse_explosion',delay=0.5,offset=1.8)
        #self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=9,cast_v_div=3,cast_spell='raise_skeleton',delay=1.2,offset=.8)
        #self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=9,cast_v_div=3,cast_spell='raise_mage',delay=1.2,offset=.8)
        pos_m = screen.convert_abs_to_monitor((-200, -200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._pather.traverse_nodes([229], self, timeout=2.5, force_tp=True, use_tp_charge=True)
        pos_m = screen.convert_abs_to_monitor((20, -50))
        self.walk(pos_m, force_move=True)
        self.poison_nova(2.0)
        pos_m = screen.convert_abs_to_monitor((50, 0))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=120,cast_div=5,cast_v_div=2,cast_spell='corpse_explosion',delay=3.0,offset=1.8)
        pos_m = screen.convert_abs_to_monitor((-30, -20))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=10,cast_v_div=4,cast_spell='raise_skeleton',delay=1.2,offset=.8)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=10,cast_v_div=4,cast_spell='raise_mage',delay=1.2,offset=.8)
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Move close to nihlathak
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8, do_pre_move=True)
        pos_m = screen.convert_abs_to_monitor((20, 20))
        self.walk(pos_m, force_move=True)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=4,cast_v_div=3,cast_spell='lower_res',delay=1.0)
        self.poison_nova(3.0)
        pos_m = screen.convert_abs_to_monitor((50, 0))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=7200,cast_div=2,cast_v_div=2,cast_spell='corpse_explosion',delay=3.0,offset=1.8)
        wait(self._cast_duration, self._cast_duration +.2)
        self.poison_nova(3.0)
        return True 

    def kill_summoner(self) -> bool:
        # Attack
        pos_m = screen.convert_abs_to_monitor((0, 30))
        self.walk(pos_m, force_move=True)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=4,cast_v_div=3,cast_spell='lower_res',delay=1.0)
        wait(0.5)
        self.poison_nova(3.0)
        pos_m = screen.convert_abs_to_monitor((50, 0))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._cast_circle(cast_dir=[-1,1],cast_start_angle=0,cast_end_angle=360,cast_div=10,cast_v_div=4,cast_spell='raise_mage',delay=1.2,offset=.8)
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
