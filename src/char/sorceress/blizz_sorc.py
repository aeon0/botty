import keyboard
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait, rotate_vec, unit_vector
import random
from pather import Location
import numpy as np
from screen import convert_abs_to_monitor, grab, convert_screen_to_abs
from config import Config
import template_finder

class BlizzSorc(Sorceress):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up Blizz Sorc")
        super().__init__(*args, **kwargs)
        #Nihlathak Bottom Right
        self._pather.offset_node(505, (50, 200))
        self._pather.offset_node(506, (40, -10))
        #Nihlathak Top Right
        self._pather.offset_node(510, (700, -55))
        self._pather.offset_node(511, (30, -25))
        #Nihlathak Top Left
        self._pather.offset_node(515, (-120, -100))
        self._pather.offset_node(517, (-18, -58))
        #Nihlathak Bottom Left
        self._pather.offset_node(500, (-150, 200))
        self._pather.offset_node(501, (10, -33))

    def _ice_blast(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.16, 0.23), spray: float = 10):
        keyboard.send(Config().char["stand_still"], do_release=False)
        if self._skill_hotkeys["ice_blast"]:
            keyboard.send(self._skill_hotkeys["ice_blast"])
        for _ in range(5):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(delay[0], delay[1])
            mouse.release(button="left")
        keyboard.send(Config().char["stand_still"], do_press=False)

    def _blizzard(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if not self._skill_hotkeys["blizzard"]:
            raise ValueError("You did not set a hotkey for blizzard!")
        keyboard.send(self._skill_hotkeys["blizzard"])
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        click_tries = random.randint(2, 4)
        for _ in range(click_tries):
            mouse.press(button="right")
            wait(0.09, 0.12)
            mouse.release(button="right")

    def kill_pindle(self) -> bool:
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        for _ in range(int(Config().char["atk_len_pindle"])):
            self._blizzard(cast_pos_abs, spray=11)
            self._ice_blast(cast_pos_abs, spray=11)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes_fixed("pindle_end", self)
        return True

    def kill_eldritch(self) -> bool:
        #move up
        pos_m = convert_abs_to_monitor((0, -175))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._blizzard((-50, -50), spray=10)
        self._cast_static()
        wait(0.75)
        #move down
        pos_m = convert_abs_to_monitor((0, 85))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._blizzard((-170, -350), spray=10)
        self._cast_static()
        #move down
        wait(0.75)
        pos_m = convert_abs_to_monitor((0, 75))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._blizzard((100, -300), spray=10)
        self._cast_static()
        wait(0.75)
        pos_m = convert_abs_to_monitor((0, 55))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._blizzard((-50, -130), spray=10)
        self._cast_static()
        wait(3.0)
        pos_m = convert_abs_to_monitor((0, -100))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._blizzard((-50, -130), spray=10)
        self._cast_static()
        wait(1.75)
        self._pather.traverse_nodes_fixed("eldritch_end", self)
        return True

    def kill_shenk(self) -> bool:
        pos_m = convert_abs_to_monitor((100, 170))
        self.pre_move()
        self.move(pos_m, force_move=True)
        #lower left posistion
        self._pather.traverse_nodes([151], self, timeout=2.5, force_tp=False)
        self._cast_static()
        self._blizzard((-250, 100), spray=10)
        self._ice_blast((60, 70), spray=60)
        self._blizzard((400, 200), spray=10)
        self._cast_static()
        self._ice_blast((-300, 100), spray=60)
        self._blizzard((185, 200), spray=10)
        pos_m = convert_abs_to_monitor((-10, 10))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_static()
        self._blizzard((-300, -270), spray=10)
        self._ice_blast((-20, 30), spray=60)
        wait(1.0)
        #teledance 2
        pos_m = convert_abs_to_monitor((150, -240))
        self.pre_move()
        self.move(pos_m, force_move=True)
        #teledance attack 2
        self._cast_static()
        self._blizzard((450, -250), spray=10)
        self._ice_blast((150, -100), spray=60)
        self._blizzard((0, -250), spray=10)
        wait(0.3)
        #Shenk Kill
        self._cast_static()
        self._blizzard((100, -50), spray=10)
        # Move to items
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.4, force_tp=True)
        return True

    def kill_council(self) -> bool:
        # Move inside to the right
        self._pather.traverse_nodes_fixed([(1110, 120)], self)
        self._pather.offset_node(300, (80, -110))
        self._pather.traverse_nodes([300], self, timeout=5.5, force_tp=True)
        self._pather.offset_node(300, (-80, 110))
        # Attack to the left
        self._blizzard((-150, 10), spray=80)
        self._ice_blast((-300, 50), spray=40)
        # Tele back and attack
        pos_m = convert_abs_to_monitor((-50, 200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._blizzard((-235, -230), spray=80)
        wait(1.0)
        pos_m = convert_abs_to_monitor((-285, -320))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        # Move to far left
        self._pather.offset_node(301, (-80, -50))
        self._pather.traverse_nodes([301], self, timeout=2.5, force_tp=True)
        self._pather.offset_node(301, (80, 50))
        # Attack to RIGHT
        self._blizzard((100, 150), spray=80)
        self._ice_blast((230, 230), spray=20)
        wait(0.5)
        self._blizzard((310, 260), spray=80)
        wait(1.0)
        # Move to bottom of stairs
        self.pre_move()
        for p in [(450, 100), (-190, 200)]:
            pos_m = convert_abs_to_monitor(p)
            self.move(pos_m, force_move=True)
        self._pather.traverse_nodes([304], self, timeout=2.5, force_tp=True)
        # Attack to center of stairs
        self._blizzard((-175, -200), spray=30)
        self._ice_blast((30, -60), spray=30)
        wait(0.5)
        self._blizzard((175, -270), spray=30)
        wait(1.0)
        # Move back inside
        self._pather.traverse_nodes_fixed([(1110, 15)], self)
        self._pather.traverse_nodes([300], self, timeout=2.5, force_tp=False)
        # Attack to center
        self._blizzard((-100, 0), spray=10)
        self._cast_static()
        self._ice_blast((-300, 30), spray=50)
        self._blizzard((-175, 50), spray=10)
        wait(1.0)
        # Move back outside and attack
        pos_m = convert_abs_to_monitor((-430, 230))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._blizzard((-50, -150), spray=30)
        self._cast_static()
        wait(0.5)
        # Move back inside and attack
        pos_m = convert_abs_to_monitor((150, -350))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Attack sequence center
        self._blizzard((-100, 35), spray=30)
        self._cast_static()
        self._blizzard((-150, 20), spray=30)
        wait(1.0)
        # Move inside
        pos_m = convert_abs_to_monitor((100, -30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Attack sequence to center
        self._blizzard((-50, 50), spray=30)
        self._cast_static()
        self._ice_blast((-30, 50), spray=10)
        # Move outside since the trav.py expects to start searching for items there if char can teleport
        self._pather.traverse_nodes([226], self, timeout=2.5, force_tp=True)
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        atk_sequences = max(1, int(Config().char["atk_len_nihlathak"]) - 1)
        for i in range(atk_sequences):
            nihlathak_pos_abs = self._pather.find_abs_node_pos(end_nodes[-1], grab())
            if nihlathak_pos_abs is not None:
                cast_pos_abs = np.array([nihlathak_pos_abs[0] * 1.0, nihlathak_pos_abs[1] * 1.0])
                wait(0.5)
                self._blizzard(cast_pos_abs, spray=0)
                wait(0.2)
                is_nihl = template_finder.search(["NIHL_BAR"], grab(), threshold=0.8, roi=Config().ui_roi["enemy_info"]).valid
                nihl_immune = template_finder.search(["COLD_IMMUNE","COLD_IMMUNES"], grab(), threshold=0.8, roi=Config().ui_roi["enemy_info"]).valid
                if is_nihl:
                    Logger.info("Found him!")
                    if nihl_immune:
                        Logger.info("Cold Immune! - Exiting")
                        return True
        wait(0.5)
        self._cast_static()
        self._blizzard(cast_pos_abs, spray=15)
        # Move to items
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8)
        return True

    def kill_summoner(self) -> bool:
        # Attack
        cast_pos_abs = np.array([0, 0])
        pos_m = convert_abs_to_monitor((-20, 20))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        for _ in range(int(Config().char["atk_len_arc"])):
            self._blizzard(cast_pos_abs, spray=11)
            self._ice_blast(cast_pos_abs, spray=11)
        wait(self._cast_duration, self._cast_duration + 0.2)
        return True


if __name__ == "__main__":
    import os
    import keyboard
    import template_finder
    from pather import Pather
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    pather = Pather()
    char = BlizzSorc(Config().blizz_sorc, Config().char, pather)
    char.kill_council()
