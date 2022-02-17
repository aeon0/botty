# f: use_wp(self, act: int, idx: int):
# - tabs (acts)
# - waypoints (rows)
from utils.custom_mouse import mouse
from utils.misc import wait
from logger import Logger

from screen import Screen
from template_finder import TemplateFinder, TemplateMatch
from ui_components import ScreenObject, Locator

_WAYPOINTS = {
    # Act 1
    "Rouge Encampment": (1, 0),
    "Cold Plains": (1, 1),
    "Stony Field": (1, 2),
    "Dark Wood": (1, 3),
    "Black Marsh": (1, 4),
    "Outer Cloister": (1, 5),
    "Jail Level 1": (1, 6),
    "Inner Cloister": (1, 7),
    "Catacombs Level 2": (1, 8),
    # Act 2
    "Lut Gholein": (2, 0),
    "Sewers Level 2": (2, 1),
    "Dry Hills": (2, 2),
    "Halls of the Dead Level 2": (2, 3),
    "Far Oasis": (2, 4),
    "Lost City": (2, 5),
    "Palace Cellar Level 1": (2, 6),
    "Arcane Sanctuary": (2, 7),
    "Canyon of the Magi": (2, 8),
    # Act 3
    "Kurast Docks": (3, 0),
    "Spider Forest": (3, 1),
    "Great Marsh": (3, 2),
    "Flayer Jungle": (3, 3),
    "Lower Kurast": (3, 4),
    "Kurast Bazaar": (3, 5),
    "Upper Kurast": (3, 6),
    "Travincal": (3, 7),
    "Durance of Hate Level 2": (3, 8),
    # Act 4
    "The Pandemonium Fortress": (4, 0),
    "City of the Damned": (4, 1),
    "River of Flame": (4, 2),
    # Act 5
    "Harrogath": (5, 0),
    "Frigid Highlands": (5, 1),
    "Arreat Plateau": (5, 2),
    "Crystalline Passage": (5, 3),
    "Glacial Trail": (5, 4),
    "Halls of Pain": (5, 5),
    "Frozen Tundra": (5, 6),
    "The Ancient's Way": (5, 7),
    "Worldstone Keep Level 2": (5, 8)
}

@Locator(ref="LABEL_WAYPOINT", roi="left_panel_label", threshold=0.8)
class WaypointLabel(ScreenObject):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        super().__init__(screen, template_finder, match)

@Locator(ref=["WP_A1_ACTIVE", "WP_A2_ACTIVE", "WP_A3_ACTIVE", "WP_A4_ACTIVE", "WP_A5_ACTIVE"], roi="left_panel_label", threshold=0.8, best_match=True)
class WaypointTabs(ScreenObject):
    def get_active_act(self):
        if self.match.name == "WP_A1_ACTIVE": act = 1
        elif self.match.name == "WP_A2_ACTIVE": act = 2
        elif self.match.name == "WP_A3_ACTIVE": act = 3
        elif self.match.name == "WP_A4_ACTIVE": act = 4
        elif self.match.name == "WP_A5_ACTIVE": act = 5
        else:
            return None
        return act

class Waypoint():
    def __init__(self, screen: Screen, template_finder: TemplateFinder) -> None:
        self._screen = screen
        self._template_finder = template_finder

    def use_wp(self, label: str = None, act: int = None, idx: int = None) -> bool:
        """
        Use Waypoint. The menu must be opened when calling the function.
        :param act: Index of the desired act starting at 1 [A1 = 1, A2 = 2, A3 = 3, ...]
        :param idx: Index of the waypoint from top. Note that it start at 0!
        """
        if label:
            act = _WAYPOINTS[label][0]
            idx = _WAYPOINTS[label][1]

        res, m = WaypointTabs.detect(self._screen, self._template_finder)
        if m.valid:
            curr_active_act = res.get_active_act()
        else:
            Logger.error("Could not find waypoint tabs")
            return False
        if curr_active_act != act:
            pos_act_btn = (self._config.ui_pos["wp_act_i_btn_x"] + self._config.ui_pos["wp_act_btn_width"] * (act - 1), self._config.ui_pos["wp_act_i_btn_y"])
            x, y = self._screen.convert_screen_to_monitor(pos_act_btn)
            mouse.move(x, y, randomize=8)
            mouse.click(button="left")
            wait(0.3, 0.4)
        pos_wp_btn = (self._config.ui_pos["wp_first_btn_x"], self._config.ui_pos["wp_first_btn_y"] + self._config.ui_pos["wp_btn_height"] * idx)
        x, y = self._screen.convert_screen_to_monitor(pos_wp_btn)
        mouse.move(x, y, randomize=[60, 9], delay_factor=[0.9, 1.4])
        wait(0.4, 0.5)
        mouse.click(button="left")
        # wait till loading screen is over
        if self.wait_for_loading_screen(5):
            while 1:
                if not self.wait_for_loading_screen(0.2):
                    return True
        return False