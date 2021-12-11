from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui_manager import UiManager
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
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(5, 5) # use Halls of Pain Waypoint (5th in A5)
        return Location.A5_NIHLATAK_LVL1_START

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        # TODO: We might need a second template for each option as merc might run into the template and we dont find it then
        template_match = self._template_finder.search_and_wait(["NI1_A", "NI1_B", "NI1_C"], threshold=0.65, time_out=20) # So let's check which layout ("NI1_A = bottom exit" , "NI1_B = large room", "NI1_C = small room") of Level1 we have.
        if not template_match.valid:# check if any of these templates was found
            return False
        if do_pre_buff:
            self._char.pre_buff()
        self._pather.traverse_nodes_fixed(template_match.name.lower(), self._char) # depending on what template is found we do static pathing to the stairs on level1. It expects that the static routes to be defined in game.ini named: "ni_a", "ni_b", "ni_c"
        self._char.select_by_template(["NI1_STAIRS"]) # So the static path brought me safely to the stairs leading to HALLS OF PAIN LEVEL2 - Now, I just have to click the stairs template "NI1_STAIRS" to enter level2        
        wait(2) #give myself the chance to walk down the stairs
        
        @dataclass
        class EyeCheckData:
            template_name: list[str]
            start_loc: Location
            end_loc: Location

        check_arr = [
            EyeCheckData(["NI2_A_SAVE_DIST"], Location.A5_NIHLATAK_LVL2_A, Location.A5_NIHLATAK_LVL2_B),
            EyeCheckData(["NI2_B_SAVE_DIST"], Location.A5_NIHLATAK_LVL2_B, Location.A5_NIHLATAK_LVL2_C),
            EyeCheckData(["NI2_C_SAVE_DIST"], Location.A5_NIHLATAK_LVL2_C, Location.A5_NIHLATAK_LVL2_D),
            EyeCheckData(["NI2_D_SAVE_DIST"], None, None),
        ]

        if not self._template_finder.search_and_wait(["NI2_SEARCH_0"], threshold=0.65, time_out=20).valid:
            return False
        if not self._pather.traverse_nodes((Location.A5_NIHLATAK_LVL2_START, Location.A5_NIHLATAK_LVL2_A), self._char, force_move=True):
            return False

        loc = Location.A5_NIHLATAK_LVL2_A

        for data in check_arr:
            template_match = self._template_finder.search_and_wait(data.template_name, threshold=0.65, time_out=4)
            if template_match.valid:
                # we should replace the fixed path with the static path i now created in game.ini.
                self._pather.traverse_nodes_fixed(template_match.name.lower(), self._char) #path to nihlatak at respective position
                break
            elif data.start_loc is not None and data.end_loc is not None:
                self._pather.traverse_nodes((data.start_loc, data.end_loc), self._char) # didnt find the eye at respective position, so go to next location to check
                loc = data.end_loc
            else:
                return False

        self._char.kill_nihlatak(loc)
        wait(0.2, 0.3)
        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A5_NIHLATAK_LVL2_END, picked_up_items)