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


class Nihlatak:
    def __init__(
        self,
        template_finder: TemplateFinder,
        pather: Pather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PickIt
    ):
        self._config = Config()
        self._template_finder = template_finder
        self._pather = pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Nihlatak")
        if not self._char.can_teleport():
            raise ValueError("Nihlatak requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(5, 5) # use Halls of Pain Waypoint (5th in A5)
        return Location.A5_NIHLATAK_START

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
        found_loading_screen_func = lambda: self._ui_manager.wait_for_loading_screen(1.0) or \
            self._template_finder.search_and_wait(["NI2_SEARCH_0", "NI2_SEARCH_1"], threshold=0.8, time_out=0.2).valid
        self._char.select_by_template(["NI1_STAIRS", "NI1_STAIRS_2", "NI1_STAIRS_3", "NI1_STAIRS_4"], found_loading_screen_func, threshold=0.63)
        # Wait until templates in lvl 2 entrance are found
        if not self._template_finder.search_and_wait(["NI2_SEARCH_0", "NI2_SEARCH_1"], threshold=0.8, time_out=20).valid:
            return False
        @dataclass
        class EyeCheckData:
            template_name: list[str]
            static_path_key: str
            static_atk_key: str

        check_arr = [
            EyeCheckData(["NI2_A_SAVE_DIST", "NI2_A_NOATTACK"], "ni2_circle_a", "ni2_a_end"),
            EyeCheckData(["NI2_B_SAVE_DIST", "NI2_B_NOATTACK"], "ni2_circle_b", "ni2_b_end"),
            EyeCheckData(["NI2_C_SAVE_DIST", "NI2_C_NOATTACK"], "ni2_circle_c", "ni2_c_end"),
            EyeCheckData(["NI2_D_SAVE_DIST", "NI2_D_NOATTACK"], "ni2_circle_d", "ni2_d_end"),
        ]

        atk_loc = None
        for data in check_arr:
            # Move to spot where eye would be visible
            self._pather.traverse_nodes_fixed(data.static_path_key, self._char)
            # Search for eye
            template_match = self._template_finder.search_and_wait(data.template_name, threshold=0.72, best_match=True, time_out=3)
            # If it is found, move down that hallway
            if template_match.valid and template_match.name.endswith("_SAVE_DIST"):
                atk_loc = data.static_atk_key
                self._pather.traverse_nodes_fixed(template_match.name.lower(), self._char)
                break

        # exit if path was not found
        if atk_loc is None:
            return False

        # Attack & Pick items
        self._char.kill_nihlatak(atk_loc)
        wait(0.2, 0.3)
        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A5_NIHLATAK_END, picked_up_items)
