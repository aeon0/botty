import keyboard
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait, rotate_vec, unit_vector
import random
from pather import Location
import numpy as np


class BlizzSorc(Sorceress):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up Blizz Sorc")
        super().__init__(*args, **kwargs)

    def _ice_blast(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.16, 0.23), spray: float = 10):
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

    def _blizzard(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if not self._skill_hotkeys["blizzard"]:
            raise ValueError("You did not set a hotkey for blizzard!")
        keyboard.send(self._skill_hotkeys["blizzard"])
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        click_tries = random.randint(2, 4)
        for _ in range(click_tries):
            mouse.press(button="right")
            wait(0.09, 0.12)
            mouse.release(button="right")

    def kill_pindle(self) -> bool:
        pindle_pos_abs = self._screen.convert_screen_to_abs(self._config.path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        for _ in range(int(self._char_config["atk_len_pindle"])):
            self._blizzard(cast_pos_abs, spray=11)
            self._ice_blast(cast_pos_abs, spray=11)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes_fixed("pindle_end", self)
        return True

    def kill_eldritch(self) -> bool:
        moves = [(0, -175), (0, 65), (0, 50)]
        for move in moves:
            pos_m = self._screen.convert_abs_to_monitor(move)
            self.pre_move()
            self.move(pos_m, force_move=True)
            self._cast_static()
            self._blizzard((10, -50), spray=40)
            self._cast_static
            wait(0.7)
        wait(1.5)
        self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, time_out=0.6, force_tp=True)
        self._blizzard((0, 0), spray=50)
        wait(1.5)
        return True

    def kill_shenk(self) -> bool:
        # Top left position
        pos_m = self._screen.convert_abs_to_monitor((100, 170))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Lower left posistion
        self._pather.traverse_nodes([151], self, time_out=2.5)
        self._cast_static()
        self._blizzard((-170, 70))
        self._ice_blast((60, 70), spray=30)
        # Teledance 1
        pos_m = self._screen.convert_abs_to_monitor((100, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Teledance attack 1
        self._cast_static()
        self._blizzard((400, 100))
        self._cast_static()
        self._blizzard((0, -250))
        wait(0.3)
        # Teledance 2
        pos_m = self._screen.convert_abs_to_monitor((150, -240))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Teledance attack 2
        self._cast_static()
        self._blizzard((-200, 75))
        wait(0.3)
        # Shenk Kill
        self._pather.traverse_nodes([151], self, time_out=2.5)
        # Shenk attack 1
        self._cast_static()
        self._blizzard((10, -70))
        wait(0.3)
        # Shenk teledance 2
        pos_m = self._screen.convert_abs_to_monitor((90, -170))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_static()
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.4, force_tp=True)
        return True

    def kill_council(self) -> bool:
        atk_len_trav = max(1, int(self._char_config["atk_len_trav"]) - 1)
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        # Go inside cast stuff in general direction
        self._pather.traverse_nodes_fixed([(1262, 265)], self)
        self._pather.offset_node(229, [350, 100])
        self._pather.traverse_nodes([229], self, time_out=2.5, force_tp=True)
        self._pather.offset_node(229, [-350, -100])
        atk_pos_abs = self._pather.find_abs_node_pos(230, self._screen.grab())
        if atk_pos_abs is None:
            Logger.debug("Could not find node [230]. Using static attack coordinates instead.")
            atk_pos_abs = [-300, -200]
        else:
            atk_pos_abs = [atk_pos_abs[0], atk_pos_abs[1] + 70]
        cast_pos_abs = np.array([atk_pos_abs[0] * 0.9, atk_pos_abs[1] * 0.9])
        cast_pos_abs_bliz = np.array([atk_pos_abs[0] * 0.25, atk_pos_abs[1] * 0.25])
        for _ in range(atk_len_trav):
            self._blizzard(cast_pos_abs_bliz, spray=120)
            self._ice_blast(cast_pos_abs, spray=90)
        self._cast_static()
        # move a bit back
        pos_m = self._screen.convert_abs_to_monitor((110, 30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        atk_pos_abs = self._pather.find_abs_node_pos(229, self._screen.grab())
        if atk_pos_abs is None:
            Logger.debug("Could not find node [229]. Using static attack coordinates instead.")
            atk_pos_abs = [-200, -80]
        self._blizzard((-70, -40), spray=50)
        self._ice_blast(cast_pos_abs, spray=60)
        # Move outside
        # Move a bit back and another round
        self._pather.traverse_nodes([226], self, time_out=2.5, force_tp=True)
        cast_pos_abs = np.array([-100, -50])
        for _ in range(atk_len_trav):
            self._blizzard(cast_pos_abs, spray=60)
            self._ice_blast(cast_pos_abs, spray=60)
        # move a bit back
        self.pre_move()
        self.move(pos_m, force_move=True)
        cast_pos_abs = np.array([-50, -100])
        for _ in range(atk_len_trav):
            self._blizzard(cast_pos_abs, spray=40)
            self._ice_blast(cast_pos_abs, spray=30)
        self._blizzard(cast_pos_abs, spray=40)
        return True

    def kill_nihlatak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        atk_sequences = max(2, int(self._char_config["atk_len_nihlatak"]) - 1)
        for i in range(atk_sequences):
            nihlatak_pos_abs = self._pather.find_abs_node_pos(end_nodes[-1], self._screen.grab())
            if nihlatak_pos_abs is not None:
                cast_pos_abs = np.array([nihlatak_pos_abs[0] * 0.9, nihlatak_pos_abs[1] * 0.9])
                self._blizzard(cast_pos_abs, spray=90)
                self._cast_static()
                # Do some tele "dancing" after each sequence
                if i < atk_sequences - 1:
                    rot_deg = random.randint(-10, 10) if i % 2 == 0 else random.randint(170, 190)
                    tele_pos_abs = unit_vector(rotate_vec(cast_pos_abs, rot_deg)) * 100
                    pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                    self.pre_move()
                    self.move(pos_m)
        # Move to items
        self._pather.traverse_nodes(end_nodes, self, time_out=0.8)
        self._blizzard((0, 0), spray=10)
        return True


if __name__ == "__main__":
    import os
    import keyboard
    from screen import Screen
    from template_finder import TemplateFinder
    from pather import Pather
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from ui import UiManager
    config = Config()
    screen = Screen(config.general["monitor"])
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
    char = BlizzSorc(config.blizz_sorc, config.char, screen, t_finder, ui_manager, pather)
    char.kill_council()
