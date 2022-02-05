from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait
from dataclasses import dataclass
from screen import Screen
import random


class Nihlathak:
    def __init__(
        self,
        screen: Screen,
        template_finder: TemplateFinder,
        pather: Pather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PickIt
    ):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._pather = pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Nihlathak")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Nihlathak requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if self._ui_manager.use_wp(5, 5): # use Halls of Pain Waypoint (5th in A5)
            return Location.A5_NIHLATHAK_START
        return False

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        # TODO: We might need a second template for each option as merc might run into the template and we dont find it then
        # Let's check which layout ("NI1_A = bottom exit" , "NI1_B = large room", "NI1_C = small room")
        template_match = self._template_finder.search_and_wait(["NI1_A", "NI1_B", "NI1_C"], threshold=0.65, time_out=20)
        if not template_match.valid:
            return False
        if do_pre_buff:
            self._char.pre_buff()

        # Depending on what template is found we do static pathing to the stairs on level1.
        # Its xpects that the static routes defined in game.ini are named: "ni1_a", "ni1_b", "ni1_c"
        self._pather.traverse_nodes_fixed(template_match.name.lower(), self._char)
        found_loading_screen_func = lambda: self._ui_manager.wait_for_loading_screen(2.0) or \
            self._template_finder.search_and_wait(["NI2_SEARCH_0", "NI2_SEARCH_1"], threshold=0.8, time_out=0.5).valid
        # look for stairs
        if not self._char.select_by_template(["NI1_STAIRS", "NI1_STAIRS_2", "NI1_STAIRS_3", "NI1_STAIRS_4"], found_loading_screen_func, threshold=0.63, time_out=4):
            # do a random tele jump and try again
            pos_m = self._screen.convert_abs_to_monitor((random.randint(-70, 70), random.randint(-70, 70)))
            self._char.move(pos_m, force_move=True)
            if not self._char.select_by_template(["NI1_STAIRS", "NI1_STAIRS_2", "NI1_STAIRS_3", "NI1_STAIRS_4"], found_loading_screen_func, threshold=0.63, time_out=4):
                return False
        # Wait until templates in lvl 2 entrance are found
        if not self._template_finder.search_and_wait(["NI2_SEARCH_0", "NI2_SEARCH_1", "NI2_SEARCH_2"], threshold=0.8, time_out=20).valid:
            return False
        wait(1.0) # wait to make sure the red writing is gone once we check for the eye
        @dataclass
        class EyeCheckData:
            template_name: list[str]
            destination_static_path_key: str
            circle_static_path_key: str
            save_dist_nodes: list[int]
            end_nodes: list[int]

        check_arr = [
            EyeCheckData(["NI2_A_1_SAFE_DIST", "NI2_A_2_SAFE_DIST", "NI2_A_1_NOATTACK", "NI2_A_2_NOATTACK"], "ni2_a_safe_dist", "ni2_circle_a", [500], [501]),
            EyeCheckData(["NI2_B_1_SAFE_DIST", "NI2_B_1_NOATTACK", "NI2_B_2_NOATTACK"], "ni2_b_safe_dist", "ni2_circle_b", [505], [506]),
            EyeCheckData(["NI2_C_1_SAFE_DIST", "NI2_C_1_NOATTACK"], "ni2_c_safe_dist", "ni2_circle_c", [510], [511]),
            EyeCheckData(["NI2_D_1_SAFE_DIST", "NI2_D_1_NOATTACK"], "ni2_d_safe_dist", "ni2_circle_d", [515], [516, 517]),
        ]

        end_nodes = None
        for data in check_arr:
            # Move to spot where eye would be visible
            self._pather.traverse_nodes_fixed(data.circle_static_path_key, self._char)
            # Search for eye
            template_match = self._template_finder.search_and_wait(data.template_name, threshold=0.7, best_match=True, time_out=3)
            # If it is found, move down that hallway
            if template_match.valid and template_match.name.endswith("_SAFE_DIST"):
                self._pather.traverse_nodes_fixed(data.destination_static_path_key, self._char)
                self._pather.traverse_nodes(data.save_dist_nodes, self._char, time_out=2, do_pre_move=False)
                end_nodes = data.end_nodes
                break

        # circle back and just assume path a if we failed to find the "eye"
        if end_nodes is None:
            self._pather.traverse_nodes_fixed("ni2_circle_back_to_a", self._char)
            self._pather.traverse_nodes_fixed(check_arr[0].destination_static_path_key, self._char)
            self._pather.traverse_nodes(check_arr[0].save_dist_nodes, self._char, time_out=2, do_pre_move=False)
            end_nodes = check_arr[0].end_nodes

        # Attack & Pick items
        if not self._char.kill_nihlathak(end_nodes):
            return False
        wait(0.2, 0.3)
        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A5_NIHLATHAK_END, picked_up_items)
