import keyboard
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait, rotate_vec, unit_vector
import random
from typing import Tuple
from pather import Location
import numpy as np


class BlizzSorc(Sorceress):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up Blizz Sorc")
        super().__init__(*args, **kwargs)

    def _left_attack(self, cast_pos_abs: Tuple[float, float], delay: float, spray: int = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["ice_blast"]:
            keyboard.send(self._skill_hotkeys["ice_blast"])
        for _ in range(5):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(delay[0], delay[1])
            mouse.release(button="left")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _right_attack(self, cast_pos_abs: Tuple[float, float], delay: float, spray: float = 10):
        keyboard.send(self._skill_hotkeys["blizzard"])
        x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
        cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        mouse.press(button="right")
        wait(delay[0], delay[1])
        mouse.release(button="right")

    def kill_pindle(self) -> bool:
        delay = [0.2, 0.3]
        if self.can_teleport():
            pindle_pos_abs = self._screen.convert_screen_to_abs(self._config.path["pindle_end"][0])
        else:
            pindle_pos_abs = self._pather.find_abs_node_pos(104, self._screen.grab())
        if pindle_pos_abs is not None:
            cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
            for _ in range(int(self._char_config["atk_len_pindle"])):
                self._right_attack(cast_pos_abs, delay, 11)
                self._left_attack(cast_pos_abs, delay, 11)
            wait(self._cast_duration, self._cast_duration + 0.2)
            # Move to items
            if self.can_teleport():
                self._pather.traverse_nodes_fixed("pindle_end", self)
            else:
                self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, force_tp=True)
            return True
        return False

    def kill_eldritch(self) -> bool:
        delay = [0.2, 0.3]
        #move up
        pos_m = self._screen.convert_abs_to_monitor((0, -175))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_static()
        #move down
        pos_m = self._screen.convert_abs_to_monitor((0, 75))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.70)
        self._right_attack((-170, -350), delay, 50)
        self._cast_static()
        #move down
        pos_m = self._screen.convert_abs_to_monitor((0, 80))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._right_attack((100, -300), delay, 20)
        self._cast_static()
        pos_m = self._screen.convert_abs_to_monitor((0, 40))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(1.0)
        self._right_attack((-50, -130), delay, 50)
        self._cast_static()
        wait(3.0)
        if self.can_teleport():
            self._pather.traverse_nodes_fixed("eldritch_end", self)
        else:
            self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, time_out=0.6, force_tp=True)
        return True

    def kill_shenk(self) -> bool:
        delay = [0.2, 0.3]
                #top left position
        pos_m = self._screen.convert_abs_to_monitor((100, 170))
        self.pre_move()
        self.move(pos_m, force_move=True)
        #lower left posistion
        self._pather.traverse_nodes([151], self, time_out=2.5, force_tp=False)
        self._cast_static()
        self._right_attack((-250, 100), delay, 10)
        self._left_attack((60, 70), delay, 30)
        self._right_attack((400, 200), delay, 10)
        self._cast_static()
        self._left_attack((-300, 100), delay, 30)
        self._right_attack((185, 200), delay, 10)
        pos_m = self._screen.convert_abs_to_monitor((-10, 10))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_static()
        self._right_attack((-300, -270), delay, 10)
        self._left_attack((-20, 30), delay, 30)
        wait(1.0)
        #teledance 2
        pos_m = self._screen.convert_abs_to_monitor((150, -240))
        self.pre_move()
        self.move(pos_m, force_move=True)
        #teledance attack 2
        self._cast_static()
        self._right_attack((450, -250), delay, 10)
        self._left_attack((150, -100), delay, 30)
        self._right_attack((0, -250), delay, 10)
        wait(0.3)
        #Shenk Kill
        self._cast_static()
        self._right_attack((100, -50), delay, 10)
        # Move to items
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.4, force_tp=True)
        return True

    def kill_council(self) -> bool:
        delay = [0.1, 0.1]
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        # Go inside cast stuff in general direction
        #node 1 middle inside
        self._pather.traverse_nodes_fixed([(1262, 265)], self)
        pos_m = self._screen.convert_abs_to_monitor((-160, -160))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._pather.traverse_nodes([300], self, time_out=2.5, force_tp=True)
        #atk_pos_abs = self._pather.find_abs_node_pos(302, self._screen.grab())
        pos_m = self._screen.convert_abs_to_monitor((100, -100))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.2)
        #attack 1
        cast_pos_abs = np.array([-270, -80])
        self._right_attack((-150, 10), delay, 80)
        self._left_attack((-300, 50), delay, 30)
        #tele back (heal merc)
        pos_m = self._screen.convert_abs_to_monitor((-50, 200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._right_attack((-235, -230), delay, 80)
        ##self._left_attack((-300, -230), delay, 30)
        wait(1.0)
        #reposistion
        pos_m = self._screen.convert_abs_to_monitor((-350, -150))
        self.pre_move()
        self.move(pos_m, force_move=True)
        #new node top left
        self._pather.traverse_nodes([301], self, time_out=2.5, force_tp=True)
        cast_pos_abs = np.array([50, 100])
        pos_m = self._screen.convert_abs_to_monitor((-115, -80))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.1)
        #attack 4
        self._right_attack((100, 100), delay, 80)
        self._left_attack((300, 200), delay, 30)
        wait(0.5)
        self._right_attack((400, 250), delay, 80)
        wait(1.0)
        #new node bottom stairs
        pos_m = self._screen.convert_abs_to_monitor((450, +100))
        self.pre_move()
        self.move(pos_m, force_move=True)
        pos_m = self._screen.convert_abs_to_monitor((-190, +200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._pather.traverse_nodes([304], self, time_out=2.5, force_tp=True)
        #Attack 5
        cast_pos_abs = np.array([-250, -350])
        self._right_attack((-175, -200), delay, 30)
        self._left_attack((30, -60), delay, 30)
        wait(0.5)
        self._right_attack((175, -270), delay, 30)
        wait(1.0)
        #noorc Kill
        pos_m = self._screen.convert_abs_to_monitor((500, -270))
        self.pre_move()
        self.move(pos_m, force_move=True)
        pos_m = self._screen.convert_abs_to_monitor((100, -70))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._pather.traverse_nodes([300], self, time_out=2.5, force_tp=False)
        #noorc attack 1
        self._right_attack((-100, 0), delay, 30)
        self._cast_static()
        self._left_attack((-300, 30), delay, 10)
        self._right_attack((-175, 50), delay, 30)
        wait(1.0)
        #noorc teledance back
        pos_m = self._screen.convert_abs_to_monitor((-430, 230))
        self.pre_move()
        self.move(pos_m, force_move=True)
        #nooric attack 3
        self._right_attack((-50, -150), delay, 30)
        self._cast_static()
        wait(0.1)
        #noorc reposition
        pos_m = self._screen.convert_abs_to_monitor((150, -350))
        self.pre_move()
        self.move(pos_m, force_move=True)
        #noorc last attack
        self._right_attack((-100, 35), delay, 30)
        self._cast_static()
        self._right_attack((-150, 20), delay, 30)
        wait(1.0)
        #noorc teledance side
        pos_m = self._screen.convert_abs_to_monitor((100, -30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        #noorc last attack 2
        self._right_attack((-50, 50), delay, 30)
        self._cast_static()
        self._left_attack((-30, 50), delay, 10)
        #wait(0.2)
        return True

    def kill_nihlatak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        delay = [0.2, 0.3]
        atk_sequences = int(self._char_config["atk_len_nihlatak"])
        for i in range(atk_sequences):
            nihlatak_pos_abs = self._pather.find_abs_node_pos(end_nodes[-1], self._screen.grab())
            if nihlatak_pos_abs is not None:
                cast_pos_abs = np.array([nihlatak_pos_abs[0] * 0.9, nihlatak_pos_abs[1] * 0.9])
                self._right_attack(cast_pos_abs, delay, 90)
                self._left_attack(cast_pos_abs, delay, 90)
                # Do some tele "dancing" after each sequence
                if i < atk_sequences - 1:
                    rot_deg = random.randint(-10, 10) if i % 2 == 0 else random.randint(170, 190)
                    tele_pos_abs = unit_vector(rotate_vec(cast_pos_abs, rot_deg)) * 100
                    pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                    self.pre_move()
                    self.move(pos_m)
        # Move to items
        self._pather.traverse_nodes(end_nodes, self, time_out=0.8)
        return True
